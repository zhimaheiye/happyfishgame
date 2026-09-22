# docs/handoff/CURRENT.md：当前任务实时交接锚点

> **注意**：本文档只记录**此时此刻**正在做的事情、当前断点与下一步。  
> 长期经验与通用规则应直接更新至 `data-model.md`、`atlas-collection.md` 或 `storage-policy.md`，禁止在此堆砌冗余历史。

---

## 一、Current Goal (当前目标)
1. [已完成] Phase 2.5 官方本体论建档（`docs/game-ontology.md`）与 Schema v0.3.0 映射；
2. [已完成] Phase 2.6 核心 Wiki 实体与采集账号主观状态彻底解耦（Schema 升至 v0.4.0，账号状态沉淀至 `data/account-observations.jsonl`）；
3. [已完成] 仓储体积与截图策略评估（`docs/playbook/storage-policy.md`）；
4. [已完成] 研发通用双向密集重叠扫描器（`scripts/ui/overlap_list_scanner.py`）；
5. [当前断点] Phase 3A-1 宝石兑换大盘双向闭环扫描达成 **114 / 124**（186 条原始 Observation，Down: 102, Up: 84，完整性报告落盘 `reports/gem-exchange-completeness.json`）；
6. [下一步接手] 补全 Gem Exchange 剩余 10 条缺口配方达成 124 完整性闭环 → 启动 Crown 98 配方采集。

---

## 二、Current Progress (当前进展)
- **图鉴基数总量**：`4331`
- **正式入库鱼类实体**：`59` 条纯净 Canonical 鱼类事实（Schema v0.4.0，无账号状态污染）
- **采集账号观察状态**：`59` 条独立账号物理观察至 `data/account-observations.jsonl`
- **宝石兑换配方数据集**：`114` 条规范化配方至 `data/gem-recipes.jsonl`（包含 `card_visual_hash` 视觉指纹与 `required_quantity` 客观需求）
- **配方卡片高保真截图**：`114` 张独立切片留存于 `raw/screenshots/gem_recipes/canonical_*.png`
- **双向扫描原始观察**：
  - Pass DOWN（Top → Bottom 密集 160px 步长）：捕获 102 张卡片
  - Pass UP（Bottom → Top 密集 160px 步长）：捕获 84 张卡片
  - 两级去重（名称 + dHash 指纹）合并：**114 条有效配方**
  - 完整性差距：当前缺口 10 条（分析表明为部分双行鱼名识别边界及尾部惯性所致）
- **完整性报告落盘**：`reports/gem-exchange-completeness.json`

---

## 三、Current Position (当前断点位置)
- **当前所处界面**：【宝石兑换】大盘页面顶部，Tab 2 (`837, 82`) 激活状态。
- **后台任务状态**：所有扫描与采集后台脚本已全部安全终止，无任何后台占用，设备处于稳定待机态。

---

## 四、Known Risks & Mitigations (已知风险与规避方案)
1. **活动弹窗干扰拦截**：
   - 现象：误点可能唤出“绿野寻仙踪”等多层活动全屏弹窗；
   - 规避：已测定活动右上角绿色圆叶 `[X]` 绝对物理坐标为 `(1815, 122)`，连击两次即可完全关闭弹窗并回到安全层级。
2. **文本输入法聚焦白条**：
   - 现象：点击搜索区域可能弹出 Android 软键盘/顶部文本条；
   - 规避：发送 `adb shell input keyevent 4`（Back 键）或点击空白区域即可退出输入态。

---

## 五、Verification Commands (现场复现与验证)
```powershell
# 1. 验证宝石兑换配方数据与卡片证据
python -c "
import json
with open('data/gem-recipes.jsonl', 'r', encoding='utf-8') as f:
    recs = [json.loads(l) for l in f if l.strip()]
print(f'Canonical Recipes: {len(recs)}')
assert len(recs) == 114
with open('reports/gem-exchange-completeness.json', 'r', encoding='utf-8') as f:
    rep = json.load(f)
print('Completeness Report:', rep['canonical_recipes'], '/', rep['expected_recipes'])
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

## 六、Next Actions (接手 Agent 立即执行动作)
1. **建立独立目标鱼集合 (Independent Target Set)**：
   - 绝不靠单纯将步长调为 120px 反复盲目重扫碰运气；
   - 先在大图鉴（4331 Atlas）中通过【标签查找】筛选【获取来源 = 宝石兑换】；
   - 提取该筛选结果下的所有目标鱼名称列表（`independent_target_set`）；
2. **集合差运算精确锁定 10 条缺口**：
   - 计算差集：`missing_names = independent_target_set - set(r['target_fish'] for r in gem_recipes)`；
   - 若 Atlas 结果恰好 124 条，证实 1-fish-1-recipe，直接根据算出的缺失鱼名定向定位并切片卡片；
   - 若 Atlas 结果少于 124 条（如 120），则证实存在一鱼多配方，防止误合并；
3. **达成 124/124 完整性证明**：
   - 结合 Top-Down 与 Bottom-Up 双向互证，生成最终无差异闭环报告；
4. **切入 Phase 3A-2**：
   - 确认无误后复用同一通用扫描器，切换至 Tab 3 (`1162, 82`) 启动皇冠兑换 98 种配方全量采集。
