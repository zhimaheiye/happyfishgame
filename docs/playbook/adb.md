# docs/playbook/adb.md：ADB 自动化工程经验底座

> 本文档汇集本项目中所有已经过实机验证的 ADB 命令、连接参数、避坑要诀与恢复方法。
> 避免未来 Agent 在环境配置和底层通信上重复消耗时间。

---

## 一、运行环境与连接参数

- **模拟器类型**：网易 MuMu 模拟器（Android 12/x86_64）
- **通信端点**：`127.0.0.1:16384`
- **屏幕物理分辨率**：`1920 x 1080`（横屏，Density 280~320）
- **已验证有效的 ADB 路径**：
  - `D:\Android\sdk\platform-tools\adb.exe`
  - `D:\platform-tools-latest-windows\platform-tools\adb.exe`
  - `D:\Program Files\Netease\MuMu\nx_main\adb.exe`

---

## 二、推荐通信模板 (Python)

为避免 Windows 命令行多进程竞争与端口争用导致 ADB daemon 频繁重启，推荐使用如下统一通信模板：

```python
import subprocess

ADB_BIN = r"D:\Android\sdk\platform-tools\adb.exe"
DEVICE = "127.0.0.1:16384"


def adb_cmd(args, check=True):
  """统一封装 ADB 执行，自动保障连接活性"""
  subprocess.run([ADB_BIN, "connect", DEVICE], capture_output=True)
  cmd = [ADB_BIN, "-s", DEVICE] + args
  res = subprocess.run(cmd, capture_output=True, text=True)
  return res.stdout.strip()
```

---

## 三、核心操作已验证指令

### 1. 截图与存证（重要避坑）
> **警告**：在 Windows PowerShell 下直接使用 `adb exec-out screencap -p > file.png` 会因为换行符 `\r\n` 转换破坏二进制 PNG 结构！必须采用设备临时路径中转后 `pull`，或在 Python 中直接读取原始字节流。

```python
def capture_screen(target_local_path):
  subprocess.run(
      [ADB_BIN, "-s", DEVICE, "shell", "screencap", "-p", "/data/local/tmp/s.png"],
      check=True,
  )
  subprocess.run(
      [ADB_BIN, "-s", DEVICE, "pull", "/data/local/tmp/s.png", target_local_path],
      check=True,
  )
```

### 2. 模拟点击 (Tap)
```python
def tap(x, y):
  subprocess.run([ADB_BIN, "-s", DEVICE, "shell", "input", "tap", str(x), str(y)])
```

### 3. 模拟滑动 (Swipe)
```python
def swipe(x1, y1, x2, y2, duration_ms=500):
  subprocess.run([
      ADB_BIN,
      "-s",
      DEVICE,
      "shell",
      "input",
      "swipe",
      str(x1),
      str(y1),
      str(x2),
      str(y2),
      str(duration_ms),
  ])
```

### 4. 返回键 (Back Keyevent)
```python
def press_back():
  subprocess.run([ADB_BIN, "-s", DEVICE, "shell", "input", "keyevent", "4"])
```

---

## 四、已知坑点与根因排查记录

### 1. uiautomator dump 无法提取控件树
- **现象**：执行 `uiautomator dump` 输出的 XML 文件仅有外层 `FrameLayout`，内层全部为 `cocos_glview`，无鱼名、按钮等 UI 文本。
- **根因**：《开心水族箱》采用 Cocos2d 自绘 OpenGL 游戏引擎，游戏内对象不是 Android 原生 View 组件。
- **对策**：不在此方向浪费时间。整体采集技术栈坚决采用 **“ADB 交互 + 视觉截图 + OCR / 多模态模型解析”**。

### 2. ADB offline 或连接丢失
- **对策**：执行前执行 `connect 127.0.0.1:16384`。若端口无响应，可尝试备用端口 `127.0.0.1:7555`。

### 3. 长列表短时滑动惯性跳卡（历史本机实测）
- **现场现象**：在历史本机实测中（网易 MuMu 模拟器 Android 12，1920×1080 环境），针对该游戏长列表（如宝石兑换大盘）执行短时 swipe（如持续时间 < 400ms）时，画面出现明显的滑移惯性（Fling），导致中间卡片跳帧遗漏。
- **实测经验**：在该现场中，将滑动持续时间拉长至 `600 ~ 800ms`（慢速拖拽），步长设定为约 `160px`（约卡片视口高度的 `0.4H ~ 0.6H`），并在每次 swipe 后暂停 `time.sleep(0.8 ~ 1.0)` 等待滑动完全静止再截图，表现显著更平稳。
- **边界说明**：此为当前游戏客户端在特定模拟器与分辨率下的实测调优经验。项目并没有引擎源码、官方文档或多环境验证证明“400ms”是所有 Cocos2d-x ScrollView 的通用阈值，严禁将此作为全局引擎定律推论。

### 4. 软键盘 / 编辑条激活时的退栈尝试（历史本机实测）
- **现场现象**：误触搜索栏等输入区域会唤出 Android 原生输入法或顶部全屏编辑栏，遮挡底层游戏视图。
- **实测经验**：在历史本机现场中，当软键盘或顶部编辑条明确处于激活焦点时，发送一次 `press_back()`（`adb shell input keyevent 4`）成功收起了输入界面且未离开当前游戏页面。
- **边界说明**：这仅是本次现场实测记录，不保证所有输入法、所有 Android ROM 或在非焦点/不同生命周期状态下都不会触发游戏内返回；不得使用“必然”或“零破坏性”等绝对定论。执行该操作后必须重新截图校验当前实际界面状态。

### 5. “绿野寻仙踪”同款活动弹窗关闭坐标（历史本机实测）
- **适用限定**：仅严格限定于 1920×1080 本机现场，且当前画面在视觉上明确出现与“绿野寻仙踪”同款的、右上角带有木桩边框绿色圆叶叉号的弹窗布局。
- **实测坐标**：在该现场截图中，该款绿色圆叶叉号的中心坐标经测定为 **`(1815, 122)`**，曾实测成功关闭该类弹窗。
- **边界与规程**：不得将此推广为“所有商业活动弹窗通用坐标”，亦不得盲目连续多次点击。推荐的标准规程为：
  1. 视觉比对或 OCR 先行确认当前确实存在该款绿色圆叶叉号关闭控件；
  2. 点击一次 `(1815, 122)`；
  3. 间隔等待并重新截图检测；
  4. 若下一层依然明确展示同款弹窗结构，方可重复单次点击；
  5. 若界面类型发生变化或未关闭，立即停止使用该固定坐标并重新评估现场。
