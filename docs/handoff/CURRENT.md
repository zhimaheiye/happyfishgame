# docs/handoff/CURRENT.md：当前任务实时交接锚点

> **注意**：本文档只记录**此时此刻**正在做的事情、当前断点与下一步。
> **项目状态（2026-10-03）**：**PAUSED / 暂停维护**。用户已明确关闭本 Wiki 项目，至少等 **2026 年考研初试结束后**才考虑重启。暂停期间不要继续运行 ADB 采集、配方扫描、数据清洗或其它推进任务；除非用户之后明确要求恢复。下文保留的是暂停前最后技术断点，供重启时接手。
> 长期经验与通用规则应直接更新至 `data-model.md`、`atlas-collection.md` 或 `storage-policy.md`，禁止在此堆砌冗余历史。

---

## 一、Current Goal (当前目标)
1. [已完成] Phase 2.5 官方本体论建档（`docs/game-ontology.md`）与 Schema v0.3.0 映射；
2. [已完成] Phase 2.6 核心 Wiki 实体与采集账号主观状态彻底解耦（Schema 升至 v0.4.0，账号状态沉淀至 `data/account-observations.jsonl`）；
3. [已完成] 仓储体积与截图策略评估（`docs/playbook/storage-policy.md`）；
4. [已完成] 研发通用双向密集重叠扫描器（`scripts/ui/overlap_list_scanner.py`）；
5. [当前断点] Phase 3A-1 宝石兑换大盘双向交叉扫描达成 **114 / 124 候选卡片**（186 条原始 Observation，Down: 102, Up: 84，完整性报告落盘 `reports/gem-exchange-completeness.json`；注：该 114 条属于初筛候选集，包含 OCR 拼接脏数据，尚未全量核验）；
6. [下一步接手] 结合大图鉴独立目标集锁定缺失项 + 重新校验清洗 114 条候选脏数据 → 达成 124 闭环验证 → 启动 Crown 98 配方采集。

---

## 二、Current Progress (当前进展)
- **图鉴基数总量**：`4331`
- **正式入库鱼类实体**：`59` 条纯净 Canonical 鱼类事实（Schema v0.4.0，无账号状态污染）
- **采集账号观察状态**：`59` 条独立账号物理观察至 `data/account-observations.jsonl`
- **宝石兑换配方候选集**：`114` 条初步候选配方至 `data/gem-recipes.jsonl`
  > [!CAUTION]
  > **数据质量现状警示**：114 条仅代表视口扫描去重后的候选卡片数量，**绝不代表 114 条配方内容已全部正确**。目前存在普遍的 OCR 错位与数字拼接（如 `required_quantity` 被误拼为 `80999`、`75667730` 等），以及鱼名截断（如 `(绿)`、`(蓝)`、`兔子鱼(雌`）。在完成切片重解析与质检前，严禁作为 Wiki 最终事实或下游工具输入。
- **配方卡片高保真截图**：`114` 张独立切片完整保留于 `raw/screenshots/gem_recipes/canonical_*.png`（作为后续重解析的唯一物理事实源，严禁删除）
- **双向扫描原始观察**：
  - Pass DOWN（Top → Bottom 密集 160px 步长）：捕获 102 张卡片
  - Pass UP（Bottom → Top 密集 160px 步长）：捕获 84 张卡片
  - 交叉去重后当前候选：**114 条**（距官方标示 124 条尚有 10 条缺口，表明两遍扫描仍存在共同盲区）
- **扫描统计报告落盘**：`reports/gem-exchange-completeness.json`（`is_complete = false`）

---

## 三、Current Position (当前断点位置)
- **当前所处界面**：【宝石兑换】大盘页面顶部，Tab 2 (`837, 82`) 激活状态。
- **后台任务状态**：所有扫描与采集后台脚本已全部安全终止，无任何后台占用，设备处于稳定待机态。

---

## 四、Known Risks & Mitigations (已知风险与规避方案)
1. **活动弹窗干扰拦截（历史本机实测经验）**：
   - 现象：误点可能唤出“绿野寻仙踪”等全屏宣传弹窗；
   - 适用限定：仅限 1920×1080 本机现场中视觉上具有同款木桩绿色圆叶叉号的弹窗；
   - 规程：视觉确认后单次点击 `(1815, 122)`，等待截图复检；若下一层仍为同款弹窗方可再次单次点击，严禁盲目连击；界面变化立即停止并重新评估。
2. **文本输入法聚焦白条（历史本机实测经验）**：
   - 现象：点击搜索区域可能弹出 Android 软键盘/顶部文本条；
   - 规程：发送 `adb shell input keyevent 4`（Back 键）尝试收起输入态。此为本机现场经验，执行后必须重新截图校验当前实际界面状态。

---

## 五、Verification Commands (现场复现与验证)
```powershell
# 1. 验证宝石兑换候选配方数据与卡片证据
python -c "
import json
with open('data/gem-recipes.jsonl', 'r', encoding='utf-8') as f:
    recs = [json.loads(l) for l in f if l.strip()]
print(f'Candidate Recipes: {len(recs)}')
assert len(recs) == 114
with open('reports/gem-exchange-completeness.json', 'r', encoding='utf-8') as f:
    rep = json.load(f)
print('Completeness Report:', rep['canonical_recipes'], '/', rep['expected_recipes'], 'is_complete:', rep['is_complete'])
"

# 2. 验证 Schema v0.4.0 纯净实体与账号观察解耦
python -c "
import json
with open('data/fish.jsonl', 'r', encoding='utf-8') as f:
    fish = [json.loads(l) for l in f if l.strip()]
with open('data/account-observations.jsonl', 'r', encoding='utf-8') as f:
    obs = [json.loads(l) for l in f if l.strip()]
print(f'Canonical Fish: {len(fish)}, Account Observations: {len(obs)}')
assert 'inventory_quantity' not in fish[0]
assert 'inventory_quantity' in obs[0]
"
```

---

## 六、Resume Actions (用户明确重启后再执行)
0. **恢复门槛**：仅在用户于考研初试结束后（或更早明确改变决定）主动要求重启本项目时，才继续以下工作；重启前先重新核验游戏版本、UI 与仓库 HEAD，不能默认 2026-09 的现场仍完全适用。
1. **建立独立目标鱼集合并做差集比对 (Independent Target Set)**：
   - 在大图鉴（4331 Atlas）中通过【标签查找】筛选【获取来源 = 宝石兑换】；
   - 遍历提取该筛选结果下的目标鱼名称列表（`independent_target_set`）；
   - 计算差集：`missing_names = independent_target_set - set(r['target_fish'] for r in gem_recipes)`；
   - **形成假设并实证检验**：数量对比仅形成假设，还需核查 Atlas 筛选是否完整、OCR 是否漏截、是否真实存在“一鱼多配方”的物理卡片；只有图文证据确凿后方可确立映射关系；
2. **缺口定向补采与扫描诊断**：
   - 针对明确缺失的鱼名在兑换列表中进行定向抓取；
   - 重新扫描（如微调步长）可作为诊断或补证手段，但不应作为唯一的闭环依赖；
3. **清洗现有 114 条候选脏数据**：
   - 利用已保存的 `raw/screenshots/gem_recipes/canonical_*.png` 高清卡片切片，重跑高精 OCR 修复 `required_quantity` 数字拼接异常（如 `80999`）与截断鱼名；
4. **达成 124 终极闭环并切入 Phase 3A-2**：
   - 生成最终无差异闭环报告后，复用同一扫描器切换至 Tab 3 (`1162, 82`) 启动皇冠兑换 98 种配方全量采集。
