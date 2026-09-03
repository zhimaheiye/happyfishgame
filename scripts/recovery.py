import subprocess
import time
import os
import datetime
from rapidocr_onnxruntime import RapidOCR

ADB_BIN = r"D:\Android\sdk\platform-tools\adb.exe"
DEVICE = "127.0.0.1:16384"

ocr_engine = None

def get_ocr():
    global ocr_engine
    if ocr_engine is None:
        ocr_engine = RapidOCR()
    return ocr_engine

def ensure_connect():
    subprocess.run([ADB_BIN, "connect", DEVICE], capture_output=True)

def adb_cmd(args, timeout=10):
    ensure_connect()
    cmd = [ADB_BIN, "-s", DEVICE] + args
    res = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if "not found" in res.stderr.lower() or "offline" in res.stderr.lower():
        ensure_connect()
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    return res

def tap(x, y):
    adb_cmd(["shell", "input", "tap", str(x), str(y)])

def capture_screen(target_path):
    target_path = os.path.abspath(target_path)
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    adb_cmd(["shell", "screencap", "-p", "/data/local/tmp/screen.png"])
    adb_cmd(["pull", "/data/local/tmp/screen.png", target_path])
    if not os.path.exists(target_path):
        raise RuntimeError(f"Failed to capture screen to {target_path}")
    return target_path

def is_atlas_ready(screenshot_path=None):
    """
    严密验证大图鉴强特征：
    1. 收集进度 / 4331
    2. 搜索 / 标签查找
    3. 右侧区段导航 100/200/300/400
    """
    tmp_shot = False
    if screenshot_path is None:
        screenshot_path = "raw/screenshots/recovery/_verify_temp.png"
        capture_screen(screenshot_path)
        tmp_shot = True

    ocr = get_ocr()
    result, _ = ocr(screenshot_path)
    texts = [r[1] for r in result] if result else []
    all_text = " ".join(texts)

    has_4331 = "4331" in all_text
    has_progress = "收集进度" in all_text or "进度" in all_text
    has_search = "搜索" in all_text or "标签查找" in all_text
    has_nav = any(num in texts for num in ["100", "200", "300", "400"])

    features = {
        "has_4331": has_4331,
        "has_progress": has_progress,
        "has_search": has_search,
        "has_nav": has_nav,
        "matched_texts": texts
    }

    # 至少满足 4331 基数以及搜索/标签/导航特征中的两项
    ready = has_4331 and (has_progress or has_search or has_nav)
    if tmp_shot and os.path.exists(screenshot_path):
        try:
            os.remove(screenshot_path)
        except Exception:
            pass
    return ready, features

def recover_to_atlas(max_attempts=2):
    """
    意外退出大图鉴的确定性恢复流程:
    0. 若当前处于次级弹窗/子页面，先点左上角返回 (70, 65) 退出到主水族箱
    1. 点击右下角宝箱 (1830, 950)
    2. 底部功能栏从左至右第 5 个书形按钮 (1195, 915)
    3. 顶栏最右侧 Tab 6 (1245, 90)
    4. 强特征判定，最多重试 1 次 (共 2 次)
    """
    for attempt in range(1, max_attempts + 1):
        print(f"[RECOVERY] 尝试执行图鉴恢复 (第 {attempt}/{max_attempts} 次)...")
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        # Step 0: 弹窗退栈（若处于详情页或仓库等，先退回到主水族箱界面）
        for _ in range(2):
            tap(70, 65)
            time.sleep(0.8)

        # Step 1: 点击右下角宝箱
        print(f"[RECOVERY] 步骤 1: 点击右下角宝箱气泡 (1830, 950)")
        tap(1830, 950)
        time.sleep(1.5)

        # Step 2: 点击从左向右第 5 个书形按钮
        print(f"[RECOVERY] 步骤 2: 点击底部第 5 个书形按钮 (1195, 915)")
        tap(1195, 915)
        time.sleep(2.0)

        # Step 3: 点击下一层最右侧按钮 (Tab 6 金色图鉴书)
        print(f"[RECOVERY] 步骤 3: 点击顶栏最右侧 Tab 6 (1260, 85)")
        tap(1260, 85)
        time.sleep(2.5)

        # Step 4: 验证特征
        shot_path = f"raw/screenshots/recovery/atlas_recovery_verify_attempt{attempt}_{ts}.png"
        capture_screen(shot_path)
        ready, features = is_atlas_ready(shot_path)

        if ready:
            success_path = f"raw/screenshots/recovery/atlas_recovery_success_{ts}.png"
            os.replace(shot_path, success_path)
            print(f"[RECOVERY] 恢复成功！状态: STATE_ATLAS_READY，截图已保存: {success_path}")
            return True, "STATE_ATLAS_READY", {
                "attempt": attempt,
                "screenshot": success_path,
                "features": features
            }
        else:
            print(f"[RECOVERY] 第 {attempt} 次恢复验证未达标: {features}")

    # 超过最大尝试次数，立即止损
    fail_shot = f"raw/screenshots/recovery/atlas_recovery_failed_{ts}.png"
    capture_screen(fail_shot)
    print(f"[RECOVERY ERROR] 连续 {max_attempts} 次恢复失败，已停止盲目操作，现场已保存至 {fail_shot}")
    return False, "STATE_BLOCKED_NEEDS_CHATGPT", {
        "attempts": max_attempts,
        "screenshot": fail_shot,
        "features": features
    }

if __name__ == "__main__":
    ready, feat = is_atlas_ready()
    print("Is Atlas Ready:", ready, feat)
    if not ready:
        recover_to_atlas()
