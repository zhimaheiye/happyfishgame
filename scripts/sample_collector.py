import json
import os
import re
import time
import sys
from datetime import datetime, timezone
from rapidocr_onnxruntime import RapidOCR
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.recovery import adb_cmd, tap, capture_screen, is_atlas_ready, recover_to_atlas

DATA_FILE = "data/fish.jsonl"
UNRESOLVED_FILE = "unresolved/unresolved.jsonl"
CHECKPOINT_FILE = "checkpoints/progress.json"

ocr_engine = None

def get_ocr():
    global ocr_engine
    if ocr_engine is None:
        ocr_engine = RapidOCR()
    return ocr_engine

def ensure_atlas_ready():
    ready, feat = is_atlas_ready()
    if not ready:
        print("[COLLECTOR] 当前不在大图鉴，尝试恢复...")
        success, state, info = recover_to_atlas()
        if not success:
            raise RuntimeError(f"Atlas recovery failed: {info}")
    return True

def parse_time_seconds(time_str):
    if not time_str:
        return None
    time_str = str(time_str).strip()
    total = 0
    m_day = re.search(r'(\d+)\s*天', time_str)
    m_hour = re.search(r'(\d+)\s*小时', time_str)
    m_min = re.search(r'(\d+)\s*分', time_str)
    m_sec = re.search(r'(\d+)\s*秒', time_str)
    if not (m_day or m_hour or m_min or m_sec):
        return None
    if m_day:
        total += int(m_day.group(1)) * 86400
    if m_hour:
        total += int(m_hour.group(1)) * 3600
    if m_min:
        total += int(m_min.group(1)) * 60
    if m_sec:
        total += int(m_sec.group(1))
    return total

def parse_crown_minutes(time_str):
    secs = parse_time_seconds(time_str)
    return (secs // 60) if secs is not None else None

def classify_acquisition_type(raw_text):
    if not raw_text:
        return ["unknown"]
    t = []
    if "商店" in raw_text or "购买" in raw_text:
        t.append("shop")
    if "宝石兑换" in raw_text:
        t.append("gem_exchange")
    elif "皇冠兑换" in raw_text:
        t.append("crown_exchange")
    elif "兑换" in raw_text:
        t.append("gem_exchange")
    if "活动" in raw_text or "节日" in raw_text:
        t.append("event")
    if "钓鱼" in raw_text or "达人" in raw_text:
        t.append("fishing")
    if "融合" in raw_text or "合成" in raw_text or "孵化" in raw_text:
        t.append("fusion")
    if "任务" in raw_text or "成长" in raw_text:
        t.append("mission")
    if not t:
        t.append("other")
    return t

def parse_detail_screenshot(shot_path):
    ocr = get_ocr()
    res, _ = ocr(shot_path)
    if not res:
        return {}

    items = []
    for box, text, score in res:
        cx = sum(p[0] for p in box) / 4
        cy = sum(p[1] for p in box) / 4
        # Dialog area
        if 480 <= cx <= 1500 and 220 <= cy <= 650:
            items.append((cy, cx, text.strip(), score))
    items.sort(key=lambda x: (x[0], x[1]))

    data = {
        "name": "",
        "category_tag": None,
        "description": None,
        "produce_time_raw": None,
        "crown_time_raw": None,
        "acquisition_raw": ""
    }

    all_lines = [item[2] for item in items]
    for i, line in enumerate(all_lines):
        if "产宝时间" in line:
            val = line.split("产宝时间")[-1].strip("：: ")
            if not val and i + 1 < len(all_lines):
                val = all_lines[i+1]
            data["produce_time_raw"] = val
        elif "皇冠时间" in line:
            val = line.split("皇冠时间")[-1].strip("：: ")
            if not val and i + 1 < len(all_lines):
                val = all_lines[i+1]
            data["crown_time_raw"] = val
        elif "获得来源" in line:
            val = line.split("获得来源")[-1].strip("：: ")
            if not val and i + 1 < len(all_lines):
                val = all_lines[i+1]
            data["acquisition_raw"] = val

    name_cands = [item for item in items if item[1] > 800 and item[0] < 340 and "收集" not in item[2] and "标签" not in item[2] and "搜索" not in item[2]]
    if name_cands:
        data["name"] = name_cands[0][2]

    tag_cands = [item for item in items if item[1] > 800 and 320 <= item[0] <= 390]
    if tag_cands:
        data["category_tag"] = " ".join([c[2] for c in tag_cands])

    desc_cands = [item for item in items if item[1] > 800 and 380 < item[0] <= 480 and "时间" not in item[2] and "来源" not in item[2]]
    if desc_cands:
        data["description"] = desc_cands[0][2]

    return data

# Card coordinates grid (2 rows x 6 cols) - Verified exact centers
COLS = [230, 510, 790, 1070, 1350, 1630]
ROWS = [410, 700]

def get_card_coords():
    coords = []
    for r in ROWS:
        for c in COLS:
            coords.append((c, r))
    return coords

def collect_sample(global_idx, card_x, card_y, section_name):
    print(f"\n[SAMPLE {global_idx}] 采集卡片 ({card_x}, {card_y}) 来自区段 {section_name}...")
    tap(card_x, card_y)
    time.sleep(1.5)

    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    shot_filename = f"sample_{global_idx:04d}_{ts}.png"
    shot_path = os.path.join("raw/screenshots", shot_filename)
    capture_screen(shot_path)

    detail = parse_detail_screenshot(shot_path)
    now_iso = datetime.now(timezone.utc).isoformat()

    # Close dialog
    tap(960, 150)
    time.sleep(0.8)

    if not detail.get("name") and not detail.get("acquisition_raw"):
        print(f"[SAMPLE {global_idx}] 识别失败或未正常打开详情弹窗，转入 unresolved")
        unres_record = {
            "atlas_index": global_idx,
            "section": section_name,
            "reason": "详情弹窗未能成功提取鱼名与获取来源",
            "screenshot": shot_path,
            "created_at": now_iso,
            "status": "pending"
        }
        with open(UNRESOLVED_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(unres_record, ensure_ascii=False) + "\n")
        return False, unres_record

    acq_type = classify_acquisition_type(detail["acquisition_raw"])
    desc = detail.get("description") or ""
    p_raw = detail.get("produce_time_raw") or ""
    c_raw = detail.get("crown_time_raw") or ""
    is_unowned = ("未解锁" in desc or "未解锁" in p_raw or "未拥有" in desc or "未拥有" in p_raw)

    collection_state = "unowned" if is_unowned else "owned"
    prod_raw = None if is_unowned else detail["produce_time_raw"]
    prod_sec = None if is_unowned else parse_time_seconds(prod_raw)
    crown_raw = None if is_unowned else (None if ("获得来源" in c_raw or "来源" in c_raw) else detail["crown_time_raw"])
    crown_min = None if is_unowned else parse_crown_minutes(crown_raw)
    final_desc = None if "未解锁" in desc else detail["description"]

    record = {
        "fish_id": None,
        "atlas_index": global_idx,
        "atlas_locator": {"section": section_name, "grid_pos": [card_x, card_y]},
        "name": detail["name"] or "未知鱼类",
        "collection_state": collection_state,
        "category_tag": detail["category_tag"],
        "description": final_desc,
        "produce_time_raw": prod_raw,
        "produce_time_seconds": prod_sec,
        "crown_time_raw": crown_raw,
        "crown_time_minutes": crown_min,
        "acquisition_raw": detail["acquisition_raw"],
        "acquisition_type": acq_type,
        "produce_items": [],
        "availability": "current" if "shop" in acq_type else "uncertain",
        "source": "in_game_atlas",
        "screenshot": shot_path.replace("\\", "/"),
        "verified_at": now_iso,
        "notes": f"区段 {section_name} 抽样样本"
    }

    with open(DATA_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

    # Also write to acquisition-methods.jsonl
    method_entry = {
        "fish_ref": record["name"],
        "method_type": acq_type[0] if acq_type else "unknown",
        "method_raw": detail["acquisition_raw"],
        "requirements_raw": None,
        "requirements": [],
        "availability": record["availability"],
        "source": "in_game_atlas",
        "screenshot": record["screenshot"],
        "verified_at": now_iso
    }
    with open("data/acquisition-methods.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(method_entry, ensure_ascii=False) + "\n")

    print(f"[SAMPLE {global_idx}] 成功入库: {record['name']} [{collection_state}] | 来源: {record['acquisition_raw']} ({record['acquisition_type']})")
    return True, record

def run_sampling(target_samples=30):
    os.makedirs("raw/screenshots", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    os.makedirs("unresolved", exist_ok=True)
    os.makedirs("checkpoints", exist_ok=True)

    ensure_atlas_ready()

    # Define sections to sample from
    # Right anchors: 1: (1795, 355), 100: (1795, 490), 200: (1795, 635), 300: (1795, 780), 400: (1795, 925)
    plan = [
        ("区段 1", (1795, 355), 12),    # 12 cards from Section 1
        ("区段 100", (1795, 490), 6),  # 6 cards from Section 100
        ("区段 200", (1795, 635), 6),  # 6 cards from Section 200
        ("区段 300", (1795, 780), 6)   # 6 cards from Section 300
    ]

    card_coords = get_card_coords()
    collected = 0
    success_count = 0
    unres_count = 0

    for sec_name, nav_coord, count in plan:
        print(f"\n==========================================")
        print(f"跳转到 {sec_name} 锚点: {nav_coord}...")
        tap(nav_coord[0], nav_coord[1])
        time.sleep(2.0)
        ensure_atlas_ready()

        for c_idx in range(count):
            if collected >= target_samples:
                break
            card_x, card_y = card_coords[c_idx]
            global_idx = collected + 1
            ok, item = collect_sample(global_idx, card_x, card_y, sec_name)
            if ok:
                success_count += 1
            else:
                unres_count += 1
            collected += 1

            # Update checkpoint
            ckpt = {
                "total_atlas_count": 4331,
                "processed_count": collected,
                "success_count": success_count,
                "unresolved_count": unres_count,
                "current_section": sec_name,
                "current_index": global_idx,
                "last_updated": datetime.now(timezone.utc).isoformat(),
                "status": "in_progress" if collected < target_samples else "completed"
            }
            with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
                json.dump(ckpt, f, ensure_ascii=False, indent=2)

            time.sleep(0.5)

    print(f"\n[DONE] 采集完成！总计: {collected}, 成功: {success_count}, 异常: {unres_count}")
    return success_count, unres_count

if __name__ == "__main__":
    run_sampling(30)
