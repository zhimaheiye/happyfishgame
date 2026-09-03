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
