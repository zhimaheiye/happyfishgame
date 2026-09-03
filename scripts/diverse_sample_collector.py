import sys
import os
import time
import json
import re
import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.recovery import tap, adb_cmd, capture_screen, get_ocr, is_atlas_ready, recover_to_atlas

DATA_FILE = "data/fish.jsonl"
METHODS_FILE = "data/acquisition-methods.jsonl"
PROGRESS_FILE = "checkpoints/progress.json"

TAG_SEARCH_BTN = (1623, 245)
CLEAR_SEL_BTN = (1152, 910)
CONFIRM_BTN = (1440, 910)
ALL_FISH_BTN = (145, 215)
CLOSE_DETAIL_BTN = (960, 150)

# Coordinates for tags in 标签查找
TAG_COORDS = {
    "magic_summon": ("魔力召唤", (1489, 698)),
    "fusion": ("融合", (1215, 615)),
    "shell_shard": ("贝壳&碎片", (1215, 698)),
    "baby_fish": ("鱼宝宝", (1488, 613)),
    "deep_sea": ("深海鱼", (667, 779)),
    "adv_school": ("高级鱼群", (1488, 416)),
    "mysterious": ("神秘鱼", (940, 415)),
    "series": ("系列鱼", (1214, 415)),
    "glowing": ("发光鱼", (667, 498))
}

CARD_COORDS = [
    (230, 410), (510, 410), (790, 410), (1070, 410), (1350, 410), (1630, 410),
    (230, 700), (510, 700), (790, 700), (1070, 700), (1350, 700), (1630, 700)
]

def parse_time_seconds(time_str):
    if not time_str:
        return None
    total = 0
    m_day = re.search(r'(\d+)\s*天', time_str)
    m_hour = re.search(r'(\d+)\s*小时', time_str)
    m_min = re.search(r'(\d+)\s*分钟', time_str)
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
    if "融合" in raw_text or "合成" in raw_text or "配方" in raw_text:
        t.append("fusion")
    if "召唤" in raw_text or "魔力" in raw_text:
        t.append("magic_summon")
    if "贝壳" in raw_text or "碎片" in raw_text or "开贝" in raw_text:
        t.append("shell_shard")
    if "深海" in raw_text:
        t.append("deep_sea")
    if "宝宝" in raw_text:
        t.append("baby_fish")
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
        elif "获得来源" in line or "来源" in line:
            val = line.split("来源")[-1].strip("：: ")
            if not val and i + 1 < len(all_lines):
                val = all_lines[i+1]
            data["acquisition_raw"] = val

    known_tags = ["真实鱼", "美食鱼", "仿物鱼", "人型鱼", "发光鱼", "神秘鱼", "系列鱼", "鱼群", "高级鱼群"]
    found_tags = []
    for line in all_lines:
        for t in known_tags:
            if t in line and t not in found_tags:
                found_tags.append(t)
    if found_tags:
        data["category_tag"] = " ".join(found_tags)

    # Name is top text in dialog
    top_candidates = [it[2] for it in items if it[0] < 340 and it[1] > 800]
    for cand in top_candidates:
        if not any(k in cand for k in known_tags) and "收集" not in cand and "进度" not in cand:
            data["name"] = cand
            break

    # Description
    desc_candidates = [it[2] for it in items if 340 <= it[0] <= 460 and it[1] > 800]
    if desc_candidates:
        data["description"] = desc_candidates[0]

    return data

def set_tag_filter(tag_key):
    label, coord = TAG_COORDS[tag_key]
    tap(TAG_SEARCH_BTN[0], TAG_SEARCH_BTN[1])
    time.sleep(1.2)
    tap(CLEAR_SEL_BTN[0], CLEAR_SEL_BTN[1])
    time.sleep(0.4)
    tap(coord[0], coord[1])
    time.sleep(0.4)
    tap(CONFIRM_BTN[0], CONFIRM_BTN[1])
    time.sleep(1.5)

def reset_filter():
    tap(ALL_FISH_BTN[0], ALL_FISH_BTN[1])
    time.sleep(1.5)

def collect_from_grid(global_idx, card_x, card_y, group_name):
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
    shot_path = f"raw/screenshots/sample_{global_idx:04d}_{ts}.png"

    tap(card_x, card_y)
    time.sleep(1.2)
    capture_screen(shot_path)

    detail = parse_detail_screenshot(shot_path)

    # Close dialog
    tap(CLOSE_DETAIL_BTN[0], CLOSE_DETAIL_BTN[1])
    time.sleep(0.8)

    if not detail or not detail.get("name"):
        return False, None

    desc = detail.get("description") or ""
    p_raw = detail.get("produce_time_raw") or ""
    c_raw = detail.get("crown_time_raw") or ""
    is_unowned = ("未解锁" in desc or "未解锁" in p_raw or "未拥有" in desc or "未拥有" in p_raw)

    collection_state = "unowned" if is_unowned else "owned"
    prod_raw = None if (is_unowned and not p_raw) else detail["produce_time_raw"]
    prod_sec = parse_time_seconds(prod_raw)
    crown_raw = None if (is_unowned and not c_raw) else (None if ("获得来源" in c_raw or "来源" in c_raw) else detail["crown_time_raw"])
    crown_min = parse_crown_minutes(crown_raw)
    final_desc = None if ("未解锁" in desc or "喜欢就" in desc) else detail["description"]

    acq_type = classify_acquisition_type(detail["acquisition_raw"])

    record = {
        "fish_id": None,
        "atlas_index": global_idx,
        "atlas_locator": {"group": group_name, "grid_pos": [card_x, card_y]},
        "name": detail["name"] or f"鱼类_{global_idx}",
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
        "availability": "current" if ("shop" in acq_type or "gem_exchange" in acq_type) else "uncertain",
        "source": "in_game_atlas",
        "screenshot": shot_path.replace("\\", "/"),
        "verified_at": now_iso,
        "notes": f"{group_name} 抽样样本"
    }

    with open(DATA_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

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
    with open(METHODS_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(method_entry, ensure_ascii=False) + "\n")

    print(f"[SAMPLE {global_idx}] {record['name']} [{collection_state}] | 标签: {record['category_tag']} | 来源: {record['acquisition_raw']} ({acq_type})")
    return True, record

def run():
    print("=== 开始第二轮多样性结构抽样 ===")
    ready, _ = is_atlas_ready()
    if not ready:
        recover_to_atlas()

    # Determine starting index
    current_count = 0
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            for l in f:
                if l.strip():
                    current_count += 1
    print(f"当前已有样本数: {current_count}")

    # Plans: sample 3~4 cards from each category/source tag
    tag_plan = [
        ("magic_summon", 4),
        ("fusion", 4),
        ("shell_shard", 4),
        ("baby_fish", 3),
        ("deep_sea", 3),
        ("adv_school", 3),
        ("mysterious", 3),
        ("series", 3),
        ("glowing", 3)
    ]

    total_collected = current_count
    for tag_key, count in tag_plan:
        group_name = TAG_COORDS[tag_key][0]
        print(f"\n--- 筛选标签: {group_name} ({tag_key}) ---")
        set_tag_filter(tag_key)

        for c_idx in range(count):
            card_x, card_y = CARD_COORDS[c_idx]
            total_collected += 1
            ok, item = collect_from_grid(total_collected, card_x, card_y, group_name)
            if not ok:
                print(f"第 {c_idx+1} 张卡片读取跳过")

        # Reset filter back to full atlas
        reset_filter()

    # Also sample 4 cards from section 400
    print("\n--- 采样区段 400 (鲸鱼族群) ---")
    tap(1795, 925) # Section 400
    time.sleep(1.5)
    for c_idx in range(4):
        card_x, card_y = CARD_COORDS[c_idx]
        total_collected += 1
        collect_from_grid(total_collected, card_x, card_y, "区段 400")

    # Update checkpoint
    checkpoint = {
        "last_updated": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "total_samples": total_collected,
        "status": "COMPLETED_ROUND_2"
    }
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(checkpoint, f, ensure_ascii=False, indent=2)

    print(f"\n=== 第二轮抽样完成！当前总样本数: {total_collected} ===")

if __name__ == "__main__":
    run()
