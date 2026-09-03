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
- **正式入库数量**：`30`（首批 30 条跨区段结构样本已全量入库 `data/fish.jsonl`，0 异常）
- **关联获取途径表**：已同步沉淀 30 条获取途径至 `data/acquisition-methods.jsonl`
- **图鉴界面状态**：`STATE_ATLAS_READY`（已验证并建立确定性恢复状态机）
- **获取类型覆盖**：`shop`（商店购买）、`gem_exchange`（宝石兑换）、`crown_exchange`（皇冠兑换）、`event`（活动获得）、`fishing`（钓鱼达人）
- **Unresolved 异常数**：`0`

---

## 三、Current Position (当前断点位置)
- **当前所处界面**：4331 全局大图鉴（区段 300 附近）。
- **模拟器状态**：MuMu 模拟器处于活跃状态（`127.0.0.1:16384`），分辨率 1920x1080。
- **自动化底座**：已建立 `scripts/recovery.py`、`scripts/sample_collector.py`、`scripts/gpt_collab.py`。

---

## 四、Current Method (当前采用方法)
- **控制与恢复链路**：Python ADB 通信 + `scripts/recovery.py` RapidOCR 强特征（4331 基数、搜索/标签、区段导航）校验。
- **数据结构链路**：
  - 鱼实体核心信息入 `data/fish.jsonl`（含 `collection_state: owned | unowned`、`acquisition_type` 细化枚举）；
  - 途径详情解耦入 `data/acquisition-methods.jsonl`；
  - 异常样本入 `unresolved/unresolved.jsonl`。

---

## 五、Current Problems (当前待解决/关注问题)
1. 现有 30 条样本覆盖区段 1～300，仍偏向头部，需展开第二轮远距离跨区段抽样（500、1000、1500、2000、2500、3000、3500、4000+）；
2. 探查“获得来源按钮后有什么”：选取代表性鱼类点击进入兑换/商城，确认具体宝石与资源需求结构；
3. 验证 `atlas_index` 与右侧锚点的真实对应关系。

---

## 六、Next Actions (下一步明确动作)
1. 将当前成果（30条样本、新脚本、工作流与模型更新）提交并 push 到 GitHub 远端；
2. 开展远距离跨区段结构抽样（500～4000+，每个区段抽选 3~5 条）；
3. 选定典型兑换鱼（如熊猫鱼、老鼠鱼）探查并记录其所需材料明细至 `data/acquisition-methods.jsonl`。
