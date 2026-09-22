# docs/data-model.md：数据模型与字段契约规范

> **版本**：v0.4.0
> **更新时间**：2026-09-03
> **核心原则**：Canonical Wiki 数据（游戏客观事实）与 Account Observation（采集账号主观状态）彻底解耦；严禁将玩家自身拥有量、点亮状态混入鱼类通用实体。

---

## 一、主实体结构：`data/fish.jsonl` (Canonical Fish Dataset)

记录游戏全局客观鱼类事实。每条记录代表图鉴中唯一的鱼类实体：

| 字段名 | 类型 | 必填 | 默认值 | 语义与规范说明 |
|---|---|---|---|---|
| `fish_id` | `string \| null` | 否 | `null` | 游戏官方唯一识别码。**若游戏内未明示官方永久ID，暂置 null，严禁 AI 自造虚假永久 ID**。 |
| `atlas_index` | `integer \| null` | 否 | `null` | 当前图鉴卡片逻辑顺位（1 ~ 4331）。 |
| `atlas_locator` | `object \| null` | 否 | `null` | 临时采集定位信息（如 `{"anchor": 100, "row": 1, "col": 1}`）。 |
| `name` | `string` | **是** | - | 鱼类名称，严格依照游戏详情页标题。 |
| `official_tags` | `string[]` | 否 | `[]` | 官方多维鱼类分类标签数组（如 `["神秘鱼", "发光鱼"]`）。 |
| `detail_category_raw` | `string \| null` | 否 | `null` | 详情弹窗直接显示的原始类别文字行。 |
| `description` | `string \| null` | 否 | `null` | 鱼类简介/特征描述文本（如“活泼，好动”）。**对于未解锁鱼类此字段为 null**。 |
| `produce_time_raw` | `string \| null` | 否 | `null` | 产宝时间原文（如 `"15秒"`、`"2小时"`）。**对于未解锁鱼类置为 `null`**。 |
| `produce_time_seconds` | `integer \| null` | 否 | `null` | 标准化产宝周期（换算为秒）。 |
| `crown_time_raw` | `string \| null` | 否 | `null` | 皇冠时间原文（如 `"60分钟"`、`"24小时"`）。**对于未解锁鱼类置为 `null`**。 |
| `crown_time_minutes` | `integer \| null` | 否 | `null` | 标准化皇冠周期（换算为分钟）。 |
| `official_acquisition_category` | `string \| null` | 否 | `null` | 游戏官方 10 大获取来源大类（官方桶：`"shop"`, `"event"`, `"fusion"`, `"baby_fish"`, `"gem_exchange"`, `"crown_exchange"`, `"shell_shard"`, `"magic_summon"`, `"deep_sea"`, `"other"`）。 |
| `acquisition_raw` | `string` | **是** | `""` | **核心证据字段**：游戏内显示的获取来源原始文字（如“商店购买”、“宝石兑换”、“钓鱼达人”）。 |
| `acquisition_type` | `string[]` | **是** | `[]` | 内部标准化获取类型细分子类（如 `["fishing"]`, `["shop"]`）。 |
| `produce_items` | `object[]` | 否 | `[]` | 产宝内容（宝物名称、产出贝币、经验数值等详情对象）。 |
| `availability` | `string` | **是** | `"unknown"` | 当前版本可获得性判定：`"current"`, `"unavailable"`, `"uncertain"`, `"unknown"`。 |
| `source` | `string` | **是** | `"in_game_atlas"` | 数据源标识（游戏图鉴为 `"in_game_atlas"`）。 |
| `screenshot` | `string` | **是** | `""` | 存证全屏/详情截图相对路径。 |
| `verified_at` | `string` | **是** | - | 采集/校验通过的 ISO-8601 时间戳。 |
| `notes` | `string \| null` | 否 | `null` | 采集补充特征与备注。 |

---

## 二、标准化枚举取值规范

### 1. 官方获取来源大类与内部细化子类
- **官方桶 (`official_acquisition_category`)**：
  `shop`, `event`, `fusion`, `baby_fish`, `gem_exchange`, `crown_exchange`, `shell_shard`, `magic_summon`, `deep_sea`, `other`。
- **内部标准化细分子类 (`acquisition_type`)**：
  `shop`, `gem_exchange`, `crown_exchange`, `event`, `fishing`（钓鱼达人，归属于官方 other 桶）、`fusion`, `magic_summon`, `shell_shard`, `baby_fish`, `deep_sea`, `mission`, `atlas_reward`（图鉴获得，归属于官方 other 桶）、`other`。

### 2. 官方鱼类分类标签 (`official_tags`)
多值数组：`"真实鱼"`, `"美食鱼"`, `"仿物鱼"`, `"人型鱼"`, `"发光鱼"`, `"神秘鱼"`, `"系列鱼"`, `"鱼群"`, `"高级鱼群"`。

### 3. 当前可用性 (`availability`)
- `current`：当前游戏内明确可以直接通过常驻手段（如商店常驻购买）获取。
- `unavailable`：当前明确已绝版或历史活动未返场。
- `uncertain`：无法从当前图鉴文字推断当前是否开放（如活动鱼、兑换鱼未探明具体要求）。
- `unknown`：缺乏任何获取渠道信息。

---

## 三、采集账号观察状态：`data/account-observations.jsonl`

为了忠实记录采集现场的物理观察（如为什么某条鱼的时间被隐藏），同时不污染 Canonical Wiki 数据，将采集账号的主观状态独立存储：

```json
{
  "fish_name": "双色巧克力鱼",
  "observed_at": "2026-09-03T21:00:00Z",
  "inventory_quantity": 1,
  "atlas_light_state": "lit",
  "collection_state_deprecated": "owned",
  "source": "collector_account_atlas",
  "screenshot": "raw/screenshots/verify_other_card1.png"
}
```

- `atlas_light_state`: `"lit"` (已点亮/已解锁) \| `"unlit"` (未点亮/未解锁，详情页显示“很遗憾，你还没有解锁这条鱼…”)
- `inventory_quantity`: 整数数值（0, 1, 88...），提取自卡片角标 `X{N}`。

---

## 四、宝石兑换配方数据集：`data/gem-recipes.jsonl`

本数据集的最终目标是全量收录游戏内 124 种宝石兑换配方，并严格区分游戏固定要求与账号背包余额：

| 字段名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `recipe_id` | `string` | **是** | 项目内部稳定生成的配方ID（如 `"gem_recipe_001"`）。 |
| `target_fish` | `string` | **是** | 目标兑换鱼类名称（如 `"雌熊猫鱼"`）。 |
| `method_type` | `string` | **是** | 固定为 `"gem_exchange"`。 |
| `requirements` | `object[]` | **是** | 所需宝石清单：`[{"resource_type": "gem", "resource_key": "gem_visual_001", "required_quantity": 30}]`。**严禁将玩家持有的数量写入 required_quantity**。 |
| `rewards` | `object[]` | **是** | 兑换产出：`[{"type": "fish", "name": "雌熊猫鱼", "quantity": 1}]`。 |
| `source` | `string` | **是** | `"in_game_gem_exchange"`。 |
| `screenshot` | `string` | **是** | 兑换卡片存证截图相对路径。 |
| `verified_at` | `string` | **是** | ISO-8601 采集时间戳。 |

> [!WARNING]
> **当前数据集数据质量现状与候选集状态提示（Phase 3A-1 阶段性说明）**：
> 当前 `data/gem-recipes.jsonl` 中暂存的 114 条记录属于自动化双向扫描生成的**初步候选/中间数据集**，114 条仅代表视口去重后的候选卡片数量，**不代表 114 条记录的内容均已经过人工或规则严密校验**：
> 1. `requirements` 中存在较普遍的 OCR 错位与数字拼接错误（如玩家持有量、相邻文本与需求量连读，导致 `required_quantity` 出现 `80999`、`75667730` 等异常大数）；
> 2. 部分 `target_fish` 存在名称截断（如 `(绿)`、`(蓝)`、`兔子鱼(雌`）；
> 3. 在完成二次精细重解析、截图回证或规则清洗前，**严禁将当前 `data/gem-recipes.jsonl` 直接作为 Wiki 最终事实或下游消费工具的可靠输入**；
> 4. `raw/screenshots/gem_recipes/` 裁剪卡片截图作为原始证据链完整保留，供后续重解析使用。


---

## 五、获取途径关联数据集：`data/acquisition-methods.jsonl`

为了支撑未来“我想兑换某条鱼，需要哪些宝石/从哪产出”的图谱查询工具：

```json
{
  "fish_ref": "雄熊猫鱼",
  "method_type": "gem_exchange",
  "method_raw": "宝石兑换",
  "requirements_raw": null,
  "requirements": [],
  "availability": "current",
  "source": "in_game",
  "screenshot": "raw/screenshots/sample_0008_xxx.png",
  "verified_at": "2026-09-03T18:00:00Z"
}
```

---

## 六、待处理队列：`unresolved/unresolved.jsonl`

遇到任何单条鱼识别异常、文字遮挡、UI 渲染残缺等情况，写入此队列以解耦自动化采集：

```json
{
  "atlas_index": 12,
  "suspected_name": "某某鱼",
  "reason": "获取方式文字被活动气泡遮挡无法可靠读取",
  "screenshot": "raw/screenshots/unresolved_0012.png",
  "created_at": "2026-09-03T18:30:00Z",
  "status": "pending"
}
```

---

## 七、Schema 演化记录 (Changelog)

### 2026-09-03 · v0.4.0 核心实体解耦与账号状态分流
- **起因**：ChatGPT 项目负责人战略审查指出：`inventory_quantity` 与 `atlas_light_state` 属于当前采集账号的主观状态，并非鱼类全局 Wiki 属性；若混在主实体中，全量 4331 采集后将难以拆分。
- **改动**：
  1. 将主表 `data/fish.jsonl` 确立为纯净的 Canonical Fish Dataset，彻底移除账号状态字段；
  2. 新增 `data/account-observations.jsonl` 独立记录采集账号观察状态；
  3. 规范宝石配方数据集 `data/gem-recipes.jsonl`：明确 `required_quantity`（游戏固定要求）与玩家当前余额解耦，严禁混淆；
  4. 修复 availability 枚举排版与章节错号问题。

### 2026-09-03 · v0.3.0 官方本体论映射与三维筛选解耦
- **起因**：实机勘测大图鉴【标签查找】系统，发现官方策划内置三大分类维度（存在状态、9大鱼分类、10大获取来源）。
- **改动**：
  1. 新增 `official_acquisition_category`，将官方“其他”桶与细化的 `fishing` 解耦；
  2. 新增 `official_tags` 数组支持多标签鱼；
  3. 建立 `docs/game-ontology.md` 官方本体论档案。

### 2026-09-03 · v0.2.0 拥有状态解耦与获取方式细化
- **改动**：引入初版 `collection_state`，明确未拥有鱼产宝时间为 null 属正常语义。

### 2026-09-03 · v0.1.0 初始骨架定义
- 确立 `acquisition_raw` 与 `acquisition_type` 彻底解耦；确立证据截图链。
