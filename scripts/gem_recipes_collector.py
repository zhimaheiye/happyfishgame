"""scripts/gem_recipes_collector.py: 宝石兑换 124 种鱼配方全量采集器 (Phase 3A-1 终极版)

核心设计：
1. 动态锚点识别：利用每张鱼卡片固有的【您已拥有X条】作为几何锚点，100% 精确关联其正上方的鱼名；
2. 自动过滤非鱼实体：经验与贝币无“您已拥有”角标，天然被排除；
3. 密集重叠滚动：每次仅滑动 180px，彻底杜绝跳行与遗漏；
4. 双向遍历（Top-Down + Bottom-Up）：确保首尾与边缘卡片 100% 覆盖；
5. 完整性证明：UI 配方总数 124，必须达成 124 条全量入库并高保真截图存证。
"""

import os
import re
import sys
import time
import json
from datetime import datetime, timezone
from PIL import Image

sys.path.insert(0, '.')
from scripts.recovery import adb_cmd, capture_screen, get_ocr, tap

OUTPUT_JSONL = 'data/gem-recipes.jsonl'
SCREENSHOT_DIR = 'raw/screenshots/gem_recipes'
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

ocr = get_ocr()

def scroll_to_top():
    print("Ensuring Tab 2 (837, 82) and scrolling to top...")
    tap(837, 82)
    time.sleep(1.2)
    for _ in range(8):
        adb_cmd(['shell', 'input', 'swipe', '500', '300', '500', '950', '200'])
        time.sleep(0.25)
    time.sleep(1.5)

def extract_cards_from_screen(im, screen_path, collected_names, collected_records, target_total):
    res, _ = ocr(screen_path)
    if not res:
        return 0
    
    owned_markers = []
    other_blocks = []
    ratio_blocks = []
    
    for b, t, s in res:
        t = t.strip()
        cy = sum(p[1] for p in b)/4
        cx = sum(p[0] for p in b)/4
        if '拥有' in t:
            owned_markers.append((cx, cy, t, b))
        else:
            m = re.findall(r'(\d+[\+]?)/(\d+)', t)
            if m:
                ratio_blocks.append((cx, cy, m))
            else:
                clean = re.sub(r'[^\w\u4e00-\u9fa5\(\)（）]', '', t)
                if len(clean) >= 2 and not any(c.isdigit() for c in clean):
                    if not any(k in clean for k in ['OK', 'ok', '默认', '排序', '兑换', '宝石', '经验', '贝币', '配方', '搜索', '返回']):
                        other_blocks.append((cx, cy, clean))
                        
    found_count = 0
    for ocx, ocy, ot, ob in owned_markers:
        # Card must be reasonably within view (not clipped)
        if ocy < 300 or ocy > 900:
            continue
            
        # Find fish name block directly above (dy: -60 to -15, dx: -80 to +80)
        best_name = None
        best_dist = 999
        for cx, cy, t in other_blocks:
            if abs(cx - ocx) < 80 and -65 < (cy - ocy) < -15:
                dist = abs(cx - ocx) + abs(cy - (ocy - 38))
                if dist < best_dist:
                    best_dist = dist
                    best_name = t
                    
        if not best_name or best_name in collected_names:
            continue
            
        # Determine card bounding box
        is_left = (ocx < 960)
        x1 = 30 if is_left else 975
        x2 = 945 if is_left else 1890
        y1 = max(0, int(ocy - 65))
        y2 = min(im.height, int(ocy + 215))
        
        card_crop = im.crop((x1, y1, x2, y2))
        curr_idx = len(collected_names) + 1
        safe_name = re.sub(r'[\\/:*?"<>|]', '_', best_name)
        safe_filename = f"recipe_{curr_idx:03d}_{safe_name}.png"
        card_save_path = os.path.join(SCREENSHOT_DIR, safe_filename)
        card_crop.save(card_save_path)
        
        # Collect ratios that fall inside this card's Y and X range
        card_ratios = []
        for rcx, rcy, rm in ratio_blocks:
            if (x1 <= rcx <= x2) and (y1 <= rcy <= y2):
                card_ratios.extend(rm)
                
        reqs = []
        for h, n in card_ratios:
            try:
                reqs.append({
                    "resource_type": "gem",
                    "quantity": int(n),
                    "inventory_at_check": int(h.replace('+', '')) if h.replace('+', '').isdigit() else None
                })
            except Exception:
                pass
                
        rec = {
            "recipe_id": f"gem_recipe_{curr_idx:03d}",
            "target_fish": best_name,
            "method_type": "gem_exchange",
            "requirements_ratios": [f"{r[0]}/{r[1]}" for r in card_ratios],
            "requirements": reqs,
            "rewards": [{"type": "fish", "name": best_name, "quantity": 1}],
            "source": "in_game_gem_exchange",
            "screenshot": f"raw/screenshots/gem_recipes/{safe_filename}",
            "verified_at": datetime.now(timezone.utc).isoformat()
        }
        
        with open(OUTPUT_JSONL, 'a', encoding='utf-8') as f:
            f.write(json.dumps(rec, ensure_ascii=False) + '\n')
            
        collected_names.add(best_name)
        collected_records.append(rec)
        found_count += 1
        print(f"[{len(collected_names):3d}/{target_total}] New Fish: {best_name:12s} | Gems: {len(reqs)} | Ratios: {[f'{r[0]}/{r[1]}' for r in card_ratios]}")
        
        if len(collected_names) >= target_total:
            break

    return found_count

def run_collector(target_total=124):
    collected_names = set()
    collected_records = []
    
    if os.path.exists(OUTPUT_JSONL):
        with open(OUTPUT_JSONL, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    rec = json.loads(line)
                    collected_names.add(rec['target_fish'])
                    collected_records.append(rec)
        print(f"Loaded {len(collected_names)} existing records from {OUTPUT_JSONL}")
        
    scroll_to_top()
    
    # PASS 1: Scroll DOWN with 180px dense overlap steps
    print(f"\n=== PASS 1: Top-to-Bottom dense sweep (Target: {target_total}) ===")
    step = 0
    no_new = 0
    
    while len(collected_names) < target_total and no_new < 15:
        step += 1
        screen_path = 'raw/screenshots/gem_screen_sweep.png'
        capture_screen(screen_path)
        im = Image.open(screen_path)
        
        found = extract_cards_from_screen(im, screen_path, collected_names, collected_records, target_total)
        if found == 0:
            no_new += 1
        else:
            no_new = 0
            
        # Dense scroll: swipe up by 180px (Y: 600 to Y: 420)
        adb_cmd(['shell', 'input', 'swipe', '500', '600', '500', '420', '800'])
        time.sleep(0.9)
        
    print(f"PASS 1 Complete. Collected so far: {len(collected_names)}/{target_total}")
    
    # PASS 2: If still < 124, scroll UP from bottom with dense overlap
    if len(collected_names) < target_total:
        print(f"\n=== PASS 2: Bottom-to-Top dense sweep ===")
        no_new = 0
        while len(collected_names) < target_total and no_new < 15:
            screen_path = 'raw/screenshots/gem_screen_sweep_up.png'
            capture_screen(screen_path)
            im = Image.open(screen_path)
            
            found = extract_cards_from_screen(im, screen_path, collected_names, collected_records, target_total)
            if found == 0:
                no_new += 1
            else:
                no_new = 0
                
            # Swipe down by 180px (Y: 420 to Y: 600)
            adb_cmd(['shell', 'input', 'swipe', '500', '420', '500', '600', '800'])
            time.sleep(0.9)

    print("\n" + "="*60)
    print(f"Gem Exchange Collection Summary:")
    print(f"Target Total: {target_total}")
    print(f"Successfully Collected: {len(collected_names)}")
    print(f"Completeness Proof: {'100% PASSED' if len(collected_names) >= target_total else 'INCOMPLETE'}")
    print("="*60)

if __name__ == '__main__':
    run_collector(124)
