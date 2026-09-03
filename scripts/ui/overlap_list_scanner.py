"""scripts/ui/overlap_list_scanner.py: 通用列表双向密集重叠扫描器

设计目标：
1. 通用性：解耦滚动逻辑与卡片解析，可同时服务于 Gem Exchange (124) 与 Crown Exchange (98)；
2. 零遗漏保证：使用 0.5H 小步长 (约 160px) 密集重叠滑动，彻底杜绝跳行；
3. 双向闭环（Bidirectional Pass）：
   - Pass A: Top → Bottom
   - Pass B: Bottom → Top
4. 两级去重合并：
   - Level 1: 目标名称规范化
   - Level 2: 视觉感知哈希 (dHash) 指纹比对
5. 自动输出 Scan Manifest 与完整性报告。
"""

import os
import sys
import time
import json
from datetime import datetime, timezone
from PIL import Image

sys.path.insert(0, '.')
from scripts.recovery import adb_cmd, capture_screen, tap

def calculate_dhash(image, hash_size=8):
    """Calculate difference hash (dHash) for visual fingerprinting."""
    resized = image.convert('L').resize((hash_size + 1, hash_size), Image.Resampling.BILINEAR)
    pixels = list(resized.getdata())
    diff = []
    for row in range(hash_size):
        for col in range(hash_size):
            pixel_left = pixels[row * (hash_size + 1) + col]
            pixel_right = pixels[row * (hash_size + 1) + col + 1]
            diff.append(pixel_left > pixel_right)
    # Convert bool array to hex string
    decimal_val = 0
    hex_string = []
    for index, value in enumerate(diff):
        if value:
            decimal_val += 2 ** (index % 4)
        if index % 4 == 3:
            hex_string.append(hex(decimal_val)[2:])
            decimal_val = 0
    return ''.join(hex_string)

class OverlapListScanner:
    def __init__(self, name: str, tab_coords=(837, 82), swipe_step_px=160, swipe_duration_ms=750):
        self.name = name
        self.tab_coords = tab_coords
        self.swipe_step_px = swipe_step_px
        self.swipe_duration_ms = swipe_duration_ms
        self.raw_observations = []
        
    def ensure_tab(self):
        if self.tab_coords:
            print(f"[{self.name}] Ensuring Tab at {self.tab_coords}...")
            tap(self.tab_coords[0], self.tab_coords[1])
            time.sleep(1.2)
            
    def scroll_to_top(self):
        print(f"[{self.name}] Scrolling to absolute top...")
        self.ensure_tab()
        for _ in range(10):
            adb_cmd(['shell', 'input', 'swipe', '500', '300', '500', '950', '180'])
            time.sleep(0.2)
        time.sleep(1.2)
        
    def scroll_to_bottom(self):
        print(f"[{self.name}] Scrolling to absolute bottom...")
        for _ in range(10):
            adb_cmd(['shell', 'input', 'swipe', '500', '950', '500', '300', '180'])
            time.sleep(0.2)
        time.sleep(1.2)
        
    def run_pass(self, direction: str, card_detector_fn, max_steps=80, max_no_new=12):
        """
        Run a single unidirectional pass with dense overlap.
        direction: 'down' (scroll down to see lower items) or 'up' (scroll up to see higher items)
        """
        print(f"\n[{self.name}] Starting Pass: {direction.upper()} (Step: {self.swipe_step_px}px)...")
        pass_observations = []
        no_new_count = 0
        step = 0
        
        seen_in_pass = set()
        
        while step < max_steps and no_new_count < max_no_new:
            step += 1
            screen_path = f'raw/screenshots/scanner_{self.name}_{direction}_step_{step:03d}.png'
            capture_screen(screen_path)
            im = Image.open(screen_path)
            
            # Detect cards in current viewport
            cards = card_detector_fn(im, screen_path, step)
            new_this_step = 0
            
            for c in cards:
                c['scan_pass'] = direction
                c['step'] = step
                c['screen_path'] = screen_path
                card_key = c.get('name_clean') or c.get('card_hash')
                if card_key not in seen_in_pass:
                    seen_in_pass.add(card_key)
                    pass_observations.append(c)
                    new_this_step += 1
                    
            if new_this_step == 0:
                no_new_count += 1
            else:
                no_new_count = 0
                
            print(f"[{direction.upper()} Step {step:2d}] Cards seen: {len(cards)} | New: {new_this_step} | Total in pass: {len(seen_in_pass)}")
            
            # Execute dense swipe
            if direction == 'down':
                y_start = 650
                y_end = y_start - self.swipe_step_px
            else:
                y_start = 350
                y_end = y_start + self.swipe_step_px
                
            adb_cmd(['shell', 'input', 'swipe', '500', str(y_start), '500', str(y_end), str(self.swipe_duration_ms)])
            time.sleep(0.8)
            
        print(f"[{self.name}] Pass {direction.upper()} Finished. Total cards: {len(pass_observations)}")
        return pass_observations

    def run_bidirectional_scan(self, card_detector_fn, target_expected=None):
        """Execute Top-to-Bottom then Bottom-to-Top, then merge & dedupe."""
        self.scroll_to_top()
        
        # Pass 1: Top to Bottom
        pass_down = self.run_pass('down', card_detector_fn)
        
        # Pass 2: Bottom to Top
        pass_up = self.run_pass('up', card_detector_fn)
        
        # Merge observations
        all_obs = pass_down + pass_up
        print(f"\n[{self.name}] Raw observations collected: {len(all_obs)} (Down: {len(pass_down)}, Up: {len(pass_up)})")
        
        # Deduplication Level 1 (Name) and Level 2 (Visual Fingerprint)
        canonical = []
        seen_names = set()
        seen_hashes = set()
        
        for obs in all_obs:
            name = obs.get('name_clean')
            vhash = obs.get('card_hash')
            
            if name and name in seen_names:
                continue
            if vhash and vhash in seen_hashes:
                continue
                
            if name:
                seen_names.add(name)
            if vhash:
                seen_hashes.add(vhash)
                
            canonical.append(obs)
            
        print(f"[{self.name}] Canonical deduplicated count: {len(canonical)} (Target: {target_expected})")
        return canonical, pass_down, pass_up
