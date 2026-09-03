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
- **正式入库数量**：`0`
- **有效抽样测试**：已成功捕获小丑鱼详情页、未拥有熊猫鱼等测试截图（存放在 `raw/screenshots/`）
- **Unresolved 异常数**：`0`

---

## 三、Current Position (当前断点位置)
- **模拟器状态**：MuMu 模拟器处于活跃状态（`127.0.0.1:16384`），位于游戏内。
- **环境验证**：ADB 通信、1920x1080 物理分辨率适配、截图与无损中转逻辑均已验证可用。
- **UI 探索**：已区分“千鱼收集”（分章节集邮）与“全局大图鉴”（4331 总量），并记录坐标体系。

---

## 四、Current Method (当前采用方法)
- **控制链路**：Python `subprocess` 调用 `platform-tools/adb.exe`。
- **解析链路**：全屏存证截图保存至 `raw/screenshots/`，经 OCR / 视觉提取后写入 `data/fish.jsonl`，异常写入 `unresolved/unresolved.jsonl`。

---

## 五、Current Problems (当前待解决/关注问题)
1. 需编写轻量级、确定性的采集脚本 `scripts/sample_collector.py`，实现“点击 -> 截图 -> 提取 -> 关闭 -> 下一条”的稳定循环。
2. 跨区段（前部 1~50、100、500、1000、2000+）验证是否存在与小丑鱼（商店直接购买）完全不同的特殊详情页模板。

---

## 六、Next Actions (下一步明确动作)
任何新 Agent 接手后，请直接执行以下动作：
1. 确认 Git 提交状态已干净；
2. 按照 `docs/workflows/atlas-collection.md` 规范编写首批抽样采集脚本；
3. 执行采集并沉淀首批 30 条样本至 `data/fish.jsonl`；
4. 校验 `docs/data-model.md` 是否需要补充新字段，并将执行进度更新回本文档。
