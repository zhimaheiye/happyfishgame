# docs/data-model.md：图鉴数据模型规范

> 本文档规范《开心水族箱》图鉴采集与沉淀的核心 Schema。  
> 数据模型随实际游戏抽样样本逐渐演化，严禁为适应过早固化的模型而扭曲真实游戏数据。

---

## 一、主数据集结构：`data/fish.jsonl`

数据采用 JSON Lines (`.jsonl`) 格式持久化，每行一条独立的结构化记录。

### 1. 基础字段定义与规范

| 字段名 | 类型 | 必填 | 默认/允许值 | 含义与使用规则 |
|---|---|---|---|---|
| `fish_id` | `string \| null` | 否 | `null` | 游戏官方唯一识别码。**若游戏内未明示官方永久ID，暂置 null，严禁 AI 自造虚假永久 ID**。 |
| `atlas_index` | `integer \| null` | 否 | `null` | 当前图鉴卡片逻辑顺位（1 ~ 4331）。 |
| `atlas_locator` | `object \| null` | 否 | `null` | 临时采集定位信息（如 `{"anchor": 100, "row": 1, "col": 1}`）。 |
| `name` | `string` | **是** | - | 鱼类名称，严格依照游戏详情页标题。 |
| `atlas_light_state` | `string` | **是** | `"unknown"` | 官方图鉴点亮状态：`"lit"`（已点亮/已解锁）、`"unlit"`（未点亮/未解锁）、`"unknown"`。 |
| `inventory_quantity` | `integer \| null` | 否 | `null` | 玩家背包/水族箱当前持有数量（来自卡片角标如 `X88` -> 88，`X0` -> 0）。 |
| `collection_state` | `string` | 否 | `"unknown"` | [已弃用/兼容保留] `"owned"` (lit) / `"unowned"` (unlit)。 |
| `official_tags` | `string[]` | 否 | `[]` | 官方多维鱼类分类标签数组（如 `["神秘鱼", "发光鱼"]`）。 |
| `detail_category_raw` | `string \| null` | 否 | `null` | 详情弹窗直接显示的原始类别文字行。 |
| `description` | `string \| null` | 否 | `null` | 鱼类简介/特征描述文本（如“活泼，好动”）。**对于未点亮鱼类此字段为 null**。 |
| `produce_time_raw` | `string \| null` | 否 | `null` | 产宝时间原文（如 `"15秒"`、`"2小时"`）。**对于 `unlit` 鱼类置为 `null`**。 |
| `produce_time_seconds` | `integer \| null` | 否 | `null` | 标准化产宝周期（换算为秒）。 |
| `crown_time_raw` | `string \| null` | 否 | `null` | 皇冠时间原文（如 `"60分钟"`、`"24小时"`）。**对于 `unlit` 鱼类置为 `null`**。 |
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

### 1. 官方图鉴点亮与持有数量 (`atlas_light_state` & `inventory_quantity`)
- `atlas_light_state`:
  - `lit`：已点亮。卡片头像彩色常亮，有皇冠/星标进度；详情页拥有完整名称、简介与产宝参数。
  - `unlit`：未点亮。卡片头像带锁头遮罩或灰暗态；详情页隐藏周期并显示“很遗憾，你还没有解锁这条鱼…”提示。
- `inventory_quantity`:
  - 整数数值（0, 1, 88...），严格解析自卡片右下角 `X{N}`。实测已证实存在“`inventory_quantity == 0` 但 `atlas_light_state == 'lit'`”的合法样本（如历史已毕业但当前无存货的星座鱼）。

### 2. 官方获取来源大类与内部细化子类
- **官方桶 (`official_acquisition_category`)**：
  `shop`, `event`, `fusion`, `baby_fish`, `gem_exchange`, `crown_exchange`, `shell_shard`, `magic_summon`, `deep_sea`, `other`。
- **内部标准化细分子类 (`acquisition_type`)**：
  `shop`, `gem_exchange`, `crown_exchange`, `event`, `fishing`（钓鱼达人，归属于官方 other 桶）、`fusion`, `magic_summon`, `shell_shard`, `baby_fish`, `deep_sea`, `mission`, `atlas_reward`（图鉴获得，归属于官方 other 桶）、`other`。

### 3. 官方鱼类分类标签 (`official_tags`)
多值数组：`"真实鱼"`, `"美食鱼"`, `"仿物鱼"`, `"人型鱼"`, `"发光鱼"`, `"神秘鱼"`, `"系列鱼"`, `"鱼群"`, `"高级鱼群"`。

---

## 三、宝石兑换配方数据集：`data/gem-recipes.jsonl`

对应 Phase 3A 专项采集，全量收录游戏内 124 种宝石兑换鱼的固定材料配方：

| 字段名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `recipe_id` | `string` | **是** | 项目内部稳定生成的配方ID（如 `"gem_recipe_001"`），非官方ID。 |
| `target_fish` | `string` | **是** | 目标兑换鱼类名称（如 `"雌熊猫鱼"`）。 |
| `method_type` | `string` | **是** | 固定为 `"gem_exchange"`。 |
| `requirements` | `object[]` | **是** | 所需宝石材料清单数组：`[{"resource_type": "gem", "resource_name_raw": "嫩绿叶宝石", "quantity": 30}]`。 |
| `rewards` | `object[]` | **是** | 兑换产出鱼：`[{"type": "fish", "name": "雌熊猫鱼", "quantity": 1}]`。 |
| `source` | `string` | **是** | `"in_game_gem_exchange"`。 |
| `screenshot` | `string` | **是** | 兑换卡片存证截图相对路径。 |
| `verified_at` | `string` | **是** | ISO-8601 采集时间戳。 |
- `current`：当前游戏内明确可以直接通过常驻手段（如商店常驻购买）获取。
- `unavailable`：当前明确已绝版或历史活动未返场。
- `uncertain`：无法从当前图鉴文字推断当前是否开放（如活动鱼、兑换鱼未探明具体要求）。
- `unknown`：缺乏任何获取渠道信息。

---

## 三、获取途径关联数据集：`data/acquisition-methods.jsonl`

为了支撑未来“我想兑换某条鱼，需要哪些宝石/从哪产出”的图谱查询工具，避免在 `fish.jsonl` 中堆砌深层嵌套，将具体获取渠道拆解沉淀至此表：

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

- 一条鱼若存在多个渠道，可写入多条对应 `fish_ref` 的独立记录。

---

## 四、待处理队列：`unresolved/unresolved.jsonl`

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

## 五、Schema 演化记录 (Changelog)

### 2026-09-03 · v0.2.0 拥有状态解耦与获取方式细化
- **起因**：首批 30 条跨区段实机抽样揭示：未拥有鱼类产宝时间被游戏提示横条替换；exchange 存在宝石兑换与皇冠兑换多种形态。
- **改动**：
  1. 新增 `collection_state: owned | unowned | unknown`，明确未拥有鱼产宝时间为 null 属正常语义，绝不进 unresolved；
  2. 细化 `acquisition_type`：拆分 `gem_exchange`、`crown_exchange`、`fishing`、`fusion`；
  3. 增加 `atlas_locator` 临时定位对象；
  4. 规范 `data/acquisition-methods.jsonl` 数据结构。

### 2026-09-03 · v0.1.0 初始骨架定义
- 确立 `acquisition_raw` 与 `acquisition_type` 彻底解耦；
- 确立 `availability` 严谨四值约束；
- 确立 `screenshot` 作为不可缺失的证据链锚点。
