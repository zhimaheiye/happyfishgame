import sys
import time
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.recovery import tap, adb_cmd, capture_screen, get_ocr

ocr = get_ocr()

# Jump to Section 1
tap(1795, 355)
time.sleep(1.5)

# Swipe 1 row (approx 290 px)
print("Starting scroll test from Section 1...")
for r in range(1, 20):
    adb_cmd(['shell', 'input', 'swipe', '960', '700', '960', '410', '400'])
    time.sleep(0.8)
    shot = f'raw/screenshots/sec1_scroll_row_{r}.png'
    capture_screen(shot)
    res, _ = ocr(shot)
    counts = [t[1] for t in res if t[1].startswith('X')]
    print(f"Row {r}: counts={counts}")
    # Check if section 100 anchor is reached or black ray appeared
    # In section 100 row 1: counts were ['X0', 'X1', 'X1', 'X1', 'X0', 'X10']
    if counts[:6] == ['X0', 'X1', 'X1', 'X1', 'X0', 'X10']:
        print(f"*** FOUND Section 100 at Row {r}! ***")
        break
