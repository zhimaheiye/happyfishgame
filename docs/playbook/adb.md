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

### 3. Cocos2d-x 滚动物理惯性（Fling）导致跳卡
- **现象**：在长列表（如 124 宝石兑换、98 皇冠兑换）执行快速 swipe 滑动时，画面出现不可预测的剧烈惯性滑移，导致中间 1~3 行卡片完全跳帧未被截图。
- **根因**：Cocos2d-x 物理滑动引擎在滑动持续时间 `< 400ms` 时触发 Fling 惯性抛掷逻辑。
- **对策**：列表扫描时必须将滑动持续时间拉长至 `600 ~ 800ms`（慢速拖拽），步长压缩至卡片高度的 `0.4H ~ 0.6H`（约 `160px`），并在每次 swipe 后设置 `time.sleep(0.8 ~ 1.0)` 等待惯性完全静止再执行 screencap。

### 4. 误点输入框触发 Android 软键盘白条
- **现象**：点击搜索栏等区域唤出 Android 原生输入法或顶部全屏编辑栏，遮挡游戏顶栏或列表。
- **对策**：执行 `press_back()`（`adb shell input keyevent 4`）。系统会优先消费 Back 事件收起键盘/编辑态，而不触发游戏内返回，操作零破坏性。

### 5. 突发商业活动全屏多层弹窗关闭
- **现象**：游戏运营期常突发“绿野寻仙踪”等全屏宣传弹窗，阻塞正常大图鉴或兑换导航。
- **实测坐标**：右上角绿色圆叶叉号的绝对物理中心为 **`(1815, 122)`**。若存在多层规则弹窗，连续发送 2~3 次该坐标点击即可完全关闭弹窗并回到游戏常规主界面。

