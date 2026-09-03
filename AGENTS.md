# AGENTS.md：开心水族箱 Wiki 项目导航

> **首要原则**：先导航，后阅读。避免每个新 Agent 盲目全盘扫描项目代码和全部截图。  
> 任何新 Agent 接手本项目，请严格按以下次序启动工作：  
> 1. 阅读 `AGENTS.md`（当前文档）定位问题域；  
> 2. 阅读 `PROJECT.md` 理解长期契约与红线；  
> 3. 阅读 `docs/handoff/CURRENT.md` 获取此时此刻的工作断点与下一步。

---

## 一、问题导航地图

| 想处理的问题 | 应阅读的文档 |
|---|---|
| 项目核心目标、长期契约、红线与工作原则 | [`PROJECT.md`](PROJECT.md) |
| 数据字段定义、Schema 演化规则、合法值 | [`docs/data-model.md`](docs/data-model.md) |
| 游戏官方分类体系、本体论与标签来源映射 | [`docs/game-ontology.md`](docs/game-ontology.md) |
| 当前采集做到哪里、此时此刻正在干什么、下一步接手 | [`docs/handoff/CURRENT.md`](docs/handoff/CURRENT.md) |
| 游戏图鉴 UI 结构、操作流、坐标与异常跳过逻辑 | [`docs/workflows/atlas-collection.md`](docs/workflows/atlas-collection.md) |
| ADB 环境配置、稳定连接、截图与点击经验、踩坑记录 | [`docs/playbook/adb.md`](docs/playbook/adb.md) |
| 外部社区/Wiki 来源可信度评估 | `docs/sources/...` |
| 已知执行失败与恢复方案 | 对应 workflow 或 playbook 文档 |
| 当前有哪些待确认/识别模糊的异常数据 | [`unresolved/unresolved.jsonl`](unresolved/unresolved.jsonl) |

---

## 二、项目目录结构

```text
d:/happyfishwiki/
├── AGENTS.md                     # [第一层] 项目入口导航（只做索引与路径指引）
├── PROJECT.md                    # [第二层] 长期契约（核心原则、数据优先级、红线）
├── docs/                         # [第三层 & 第四层] 长期专业档案与实时接手
│   ├── data-model.md             # 数据模型、字段规范与演化历史
│   ├── workflows/                # 业务工作流规程（如图鉴采集 atlas-collection.md）
│   ├── playbook/                 # 工程经验底座（如 adb.md、识别踩坑等）
│   ├── sources/                  # 外部数据源可信度档案
│   └── handoff/
│       └── CURRENT.md            # [第四层] 实时交接锚点（只记录当前这一刻）
├── data/                         # 结构化成果数据
│   ├── fish.jsonl                # 鱼类核心数据
│   └── acquisition-methods.jsonl # 获取途径关联数据
├── raw/                          # 原始证据底料（不可随意删除）
│   ├── screenshots/              # 原始全屏及关键裁剪截图
│   └── dump.xml                  # 辅助层级 dump 留存
├── checkpoints/                  # 任务持久化断点
│   └── progress.json             # 自动化采集进度持久化状态
├── unresolved/                   # 异常与模糊样本暂存（不阻塞主流程）
│   └── unresolved.jsonl          # 待排查/清洗队列
├── logs/                         # 运行与会话日志
│   └── sessions/                 # 历史会话及采集流水
└── scripts/                      # 采集与清洗实用自动化工具
```

---

## 三、极简执行与验证命令

### 1. 验证 ADB 连接与环境
```powershell
python -c "
import subprocess
adb = r'D:\Android\sdk\platform-tools\adb.exe'
subprocess.run([adb, 'connect', '127.0.0.1:16384'], capture_output=True)
res = subprocess.run([adb, '-s', '127.0.0.1:16384', 'shell', 'wm', 'size'], capture_output=True, text=True)
print(res.stdout.strip())
"
# 预期输出: Physical size: 1080x1920 (横屏 1920x1080)
```

### 2. 获取实时截图存证
```powershell
python -c "
import subprocess
adb = r'D:\Android\sdk\platform-tools\adb.exe'
subprocess.run([adb, '-s', '127.0.0.1:16384', 'shell', 'screencap', '-p', '/data/local/tmp/screen.png'])
subprocess.run([adb, '-s', '127.0.0.1:16384', 'pull', '/data/local/tmp/screen.png', 'raw/screenshots/current_verify.png'])
print('Screenshot saved to raw/screenshots/current_verify.png')
"
```

---

## 四、核心纪律摘要

1. **没有真正需要用户决策的问题，不得停机**：单条识别模糊、点空、偶发网络异常，统统存入 `unresolved/` 继续推进。
2. **“继续执行”优先于“汇报后等待”**：汇报不等于停止；目标明确、步骤安全时，保持自动化或分析的连续推进。
3. **永远留下接手锚点**：任何批处理必须随时可中断可恢复；阶段成果必须落入 `CURRENT.md` 和 `checkpoints/`。
4. **避免过度工程化**：文档和工具全心全意服务于 4331 条图鉴数据的采集与沉淀，拒绝虚空设计复杂抽象层。
