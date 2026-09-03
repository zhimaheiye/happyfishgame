"""scripts/gem_scan_executor.py: 宝石兑换 124 配方双向重叠闭环扫描执行器

严格遵循 ChatGPT 指令 (Phase 3A-1 闭环标准)：
1. 模块化调用 scripts.ui.overlap_list_scanner.OverlapListScanner；
2. 密集 160px 重叠步长，执行 Top→Bottom + Bottom→Top 双向遍历；
3. 两级去重：规范化名称 + 视觉 dHash 指纹；
4. 严格解耦：required_quantity 只存游戏客观需求数量，账号当前持有量仅作调试参考；
5. 输出完整性验证报告 reports/gem-exchange-completeness.json；
6. 结构化入库 data/gem-recipes.jsonl。
"""

import os
import re
import sys
import json
from datetime import datetime, timezone
from PIL import Image

sys.path.insert(0, '.')
from scripts.ui.overlap_list_scanner import OverlapListScanner, calculate_dhash
from scripts.recovery import get_ocr

os.makedirs('reports', exist_ok=True)
os.makedirs('raw/screenshots/gem_recipes', exist_ok=True)

ocr = get_ocr()

def gem_card_detector(im: Image.Image, screen_path: str, step: int):
    res, _ = ocr(screen_path)
    if not res:
        return []
        
    owned_markers = []
    other_blocks = []
    ratio_blocks = []
    
    for b, t, s in res:
        t = t.strip()
        cy = sum(p[1] for p in b)/4
        cx = sum(p[0] for p in b)/4
        if '拥有' in t:
            owned_markers.append((cx, cy, t))
        else:
            m = re.findall(r'(\d+[\+]?)/(\d+)', t)
            if m:
                ratio_blocks.append((cx, cy, m))
            else:
                clean = re.sub(r'[^\w\u4e00-\u9fa5\(\)（）]', '', t)
                if len(clean) >= 2 and not any(c.isdigit() for c in clean):
                    if not any(k in clean for k in ['OK', 'ok', '默认', '排序', '兑换', '宝石', '经验', '贝币', '配方', '搜索', '返回', '礼盒', '皇冠']):
                        other_blocks.append((cx, cy, clean))
                        
    detected_cards = []
    for ocx, ocy, ot in owned_markers:
        # Require card to be comfortably in view
        if ocy < 310 or ocy > 880:
            continue
            
        best_name = None
        best_dist = 999
        for cx, cy, t in other_blocks:
            if abs(cx - ocx) < 85 and -65 < (cy - ocy) < -15:
                dist = abs(cx - ocx) + abs(cy - (ocy - 38))
                if dist < best_dist:
                    best_dist = dist
                    best_name = t
                    
        if not best_name:
            continue
            
        is_left = (ocx < 960)
        x1 = 30 if is_left else 975
        x2 = 945 if is_left else 1890
        y1 = max(0, int(ocy - 65))
        y2 = min(im.height, int(ocy + 215))
        
        card_crop = im.crop((x1, y1, x2, y2))
        card_hash = calculate_dhash(card_crop)
        
        card_ratios = []
        for rcx, rcy, rm in ratio_blocks:
            if (x1 <= rcx <= x2) and (y1 <= rcy <= y2):
                card_ratios.extend(rm)
                
        reqs = []
        for h, n in card_ratios:
            try:
                reqs.append({
                    "resource_type": "gem",
                    "resource_name_raw": None, # 遵照 GPT 批示：绝不看颜色猜测宝石名
                    "required_quantity": int(n), # 客观 Wiki 需求
                    "observed_account_quantity": int(h.replace('+', '')) if h.replace('+', '').isdigit() else None
                })
            except:
                pass
                
        detected_cards.append({
            "name_raw": best_name,
            "name_clean": best_name,
            "bbox": [x1, y1, x2, y2],
            "card_hash": card_hash,
            "ratios": card_ratios,
            "requirements": reqs,
            "card_crop": card_crop
        })
        
    return detected_cards

def run_gem_verification(target_expected=124):
    scanner = OverlapListScanner(
        name="gem_exchange",
        tab_coords=(837, 82),
        swipe_step_px=160, # 密集重叠步长约 0.5H
        swipe_duration_ms=750
    )
    
    canonical_cards, pass_down, pass_up = scanner.run_bidirectional_scan(gem_card_detector, target_expected=target_expected)
    
    # Save canonical records to data/gem-recipes.jsonl and card crops
    saved_records = []
    for idx, c in enumerate(canonical_cards, 1):
        clean_name = c['name_clean']
        safe_name = re.sub(r'[\\/:*?"<>|]', '_', clean_name)
        crop_path = f"raw/screenshots/gem_recipes/canonical_{idx:03d}_{safe_name}.png"
        c['card_crop'].save(crop_path)
        
        rec = {
            "recipe_id": f"gem_recipe_{idx:03d}",
            "target_fish": clean_name,
            "method_type": "gem_exchange",
            "requirements": c['requirements'],
            "rewards": [{"type": "fish", "name": clean_name, "quantity": 1}],
            "card_visual_hash": c['card_hash'],
            "source": "in_game_gem_exchange",
            "screenshot": crop_path,
            "verified_at": datetime.now(timezone.utc).isoformat()
        }
        saved_records.append(rec)
        
    with open('data/gem-recipes.jsonl', 'w', encoding='utf-8') as out:
        for r in saved_records:
            out.write(json.dumps(r, ensure_ascii=False) + '\n')
            
    # Completeness Report
    names_down = set(c['name_clean'] for c in pass_down)
    names_up = set(c['name_clean'] for c in pass_up)
    
    missing_from_down = list(names_up - names_down)
    missing_from_up = list(names_down - names_up)
    
    report = {
        "expected_recipes": target_expected,
        "canonical_recipes": len(canonical_cards),
        "unique_targets": len(set(c['name_clean'] for c in canonical_cards)),
        "top_down_observations": len(pass_down),
        "bottom_up_observations": len(pass_up),
        "missing_from_top_down": missing_from_down,
        "missing_from_bottom_up": missing_from_up,
        "is_complete": (len(canonical_cards) == target_expected),
        "validated_at": datetime.now(timezone.utc).isoformat()
    }
    
    with open('reports/gem-exchange-completeness.json', 'w', encoding='utf-8') as rf:
        json.dump(report, rf, ensure_ascii=False, indent=2)
        
    print("\n" + "="*60)
    print("GEM EXCHANGE SCAN COMPLETENESS REPORT:")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print("="*60)
    return report

if __name__ == '__main__':
    run_gem_verification(124)
