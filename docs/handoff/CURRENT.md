# docs/handoff/CURRENT.md：当前任务实时交接锚点

> **注意**：本文档只记录**此时此刻**正在做的事情、当前断点与下一步。  
> 长期经验与通用规则应直接更新至 `data-model.md`、`atlas-collection.md` 或 `adb.md`，禁止在此堆砌冗余历史。

---

## 一、Current Goal (当前目标)
1. 建立并落盘项目的四层解耦文档与规范体系（AGENTS.md、PROJECT.md、data-model.md、atlas-collection.md、adb.md、CURRENT.md）。
2. 初始化工程底座与 Git 仓储并完成首版提交。
3. 准备执行第一阶段任务：在 4331 大图鉴中跨区段采集 30 条“结构样本”，验证详情页模板与数据字段覆盖度。

---

## 二、Current Progress (当前进展)
- **图鉴基数总量**：`4331`
- **正式入库数量**：`59`（覆盖全系统 10 大获取来源与 9 大鱼类标签，数据 100% 结构化清洗入库）
- **关联获取途径表**：已沉淀 59 条获取途径明细至 `data/acquisition-methods.jsonl`
- **图鉴界面状态**：`STATE_ATLAS_READY`（已像素级校验 Tab 6 坐标 `(1260, 85)` 与弹窗退栈防护）
- **获取类型全覆盖（10/10）**：
  - `shop`（商店购买: 27条）
  - `gem_exchange`（宝石兑换: 7条）
  - `crown_exchange`（皇冠兑换: 1条）
  - `event`（活动获得: 3条）
  - `fishing`（钓鱼达人: 3条）
  - `magic_summon`（魔力召唤: 4条）
  - `fusion`（限时融合: 4条）
  - `shell_shard`（开贝壳: 4条）
  - `baby_fish`（鱼宝宝: 3条）
  - `deep_sea`（深海鱼: 3条）
- **已探明“获得来源”次级系统（8/8 全安全返回验证）**：
  1. `shop` -> 商店单鱼页（饥饿时间、单价贝币），左上 `返回 (70, 65)` 安全返回；
  2. `gem_exchange` -> 宝石兑换大盘（124 种配方明细），左上 `返回 (70, 65)` 安全返回；
  3. `crown_exchange` -> 皇冠兑换大盘（98 种配方，皇冠鱼原材料），左上 `返回 (70, 65)` 安全返回；
  4. `event` -> 活动未开启呈置灰态，弹窗无损留存；
  5. `fishing` -> 钓鱼达人大地图，右上红色 `[X] (1870, 70)` 安全返回原图鉴位置；
  6. `magic_summon` -> 召唤祭坛（初级 200 绿水晶 / 高级 60 粉+500 绿），左上 `返回 (70, 65)` 安全返回；
  7. `shell_shard` -> 开贝壳界面（普通贝壳 / 金贝壳），左上 `返回 (70, 65)` 安全返回；
  8. `fusion` -> 章鱼博士配方与熔炉（3 位复合公式），模态右上 `[X] (1765, 165)` + 左上 `返回 (70, 65)` 安全返回。

---

## 三、Current Position (当前断点位置)
- **当前所处界面**：4331 全局大图鉴顶层视图，未筛选全部鱼种状态。
- **模拟器状态**：MuMu 模拟器处于活跃状态（`127.0.0.1:16384`），横屏 1920x1080。
- **自动化脚本**：
  - `scripts/recovery.py`：支持模态自动退栈与 Tab 6 精确定位 `(1260, 85)`；
  - `scripts/diverse_sample_collector.py`：基于官方标签体系的精准抽样器；
  - `scripts/do_report.py`：与 ChatGPT Web 端双向协同信使。

---

## 四、Current Method (当前采用方法)
- **控制与恢复链路**：Python ADB 通信 + `scripts/recovery.py` RapidOCR 强特征（4331 基数、搜索/标签、区段导航）校验。
- **数据结构链路**：
  - 鱼实体核心信息入 `data/fish.jsonl`（含 `collection_state: owned | unowned`、`acquisition_type` 细化枚举）；
  - 途径详情解耦入 `data/acquisition-methods.jsonl`；
  - 异常样本入 `unresolved/unresolved.jsonl`。

---

## 五、Current Problems (当前待解决/关注问题)
2. 探查“获得来源按钮后有什么”：选取代表性鱼类点击进入兑换/商城，确认具体宝石与资源需求结构；
3. 验证 `atlas_index` 与右侧锚点的真实对应关系。

---

## 六、Next Actions (下一步明确动作)
1. 将当前成果（30条样本、新脚本、工作流与模型更新）提交并 push 到 GitHub 远端；
2. 开展远距离跨区段结构抽样（500～4000+，每个区段抽选 3~5 条）；
3. 选定典型兑换鱼（如熊猫鱼、老鼠鱼）探查并记录其所需材料明细至 `data/acquisition-methods.jsonl`。
