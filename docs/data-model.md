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
| `atlas_locator` | `object \| null` | 否 | `null` | 临时采集定位信息（如 `{"anchor": 100, "row": 1, "col": 1}`），在未确切证明全局严格连续序号前使用。 |
| `name` | `string` | **是** | - | 鱼类名称，严格依照游戏详情页标题。 |
| `collection_state` | `string` | **是** | `"unknown"` | 玩家拥有/解锁状态：`"owned"`（已拥有）、`"unowned"`（未拥有/未解锁）、`"unknown"`。 |
| `category_tag` | `string \| null` | 否 | `null` | 详情页显示的类别标签（例如：“真实鱼”、“神话鱼”等）。 |
| `description` | `string \| null` | 否 | `null` | 鱼类简介/特征描述文本（如“活泼，好动”）。 |
| `produce_time_raw` | `string \| null` | 否 | `null` | 产宝时间原文（如 `"15秒"`、`"2小时"`）。**对于 `unowned` 鱼类，游戏隐藏此时段，应明确置为 `null`，严禁进 unresolved**。 |
| `produce_time_seconds` | `integer \| null` | 否 | `null` | 标准化产宝周期（换算为秒）。转换失败或无法确认时填 `null`。 |
| `crown_time_raw` | `string \| null` | 否 | `null` | 皇冠时间原文（如 `"60分钟"`、`"24小时"`）。**对于 `unowned` 鱼类置为 `null`**。 |
| `crown_time_minutes` | `integer \| null` | 否 | `null` | 标准化皇冠周期（换算为分钟）。 |
| `acquisition_raw` | `string` | **是** | `""` | **核心证据字段**：游戏内显示的获取来源全部原始文字（如“商店购买”、“宝石兑换”、“参加XXXX活动获得”）。 |
| `acquisition_type` | `string[]` | **是** | `[]` | 标准化获取类型列表（支持多对多），参见下方细化枚举。 |
| `produce_items` | `object[]` | 否 | `[]` | 产宝内容（宝物名称、产出贝币、经验数值等详情对象）。 |
| `availability` | `string` | **是** | `"unknown"` | 当前版本可获得性判定，只允许合法状态枚举。 |
| `source` | `string` | **是** | `"in_game_atlas"` | 数据源标识（游戏图鉴为 `"in_game_atlas"`）。 |
| `screenshot` | `string` | **是** | `""` | 存证全屏/详情截图相对路径（如 `"raw/screenshots/sample_0001_xxx.png"`）。 |
| `verified_at` | `string` | **是** | - | 采集/校验通过的 ISO-8601 时间戳（如 `"2026-09-03T18:00:00Z"`）。 |
| `notes` | `string \| null` | 否 | `null` | 采集过程中的特征补充、异常标记或特殊观察。 |

---

## 二、标准化枚举取值规范

### 1. 拥有与解锁状态 (`collection_state`)
- `owned`：玩家已拥有该鱼（卡片显示具体拥有数量如 X88，详情展示产宝与皇冠时间）。
- `unowned`：玩家未拥有/未解锁该鱼（卡片显示 X0 或锁头，详情展示“很遗憾，你还没有解锁这条鱼…”横条提示，产宝/皇冠时间被游戏官方隐藏）。
- `unknown`：状态无法判定。

> [!NOTE]
> **UI 语义与数据质量红线**：未拥有鱼的产宝与皇冠时间被游戏隐藏属于**正常预期行为**，此时 `produce_time_raw: null`，**严禁**因此将样本判定为识别失败而丢入 `unresolved`。只有当鱼为 `owned` 且字段区域被遮挡、渲染残缺时，才属于真正的识别异常。

### 2. 获取方式标准化分类 (`acquisition_type`)
根据游戏官方标签体系与实机采样细化分类：
- `shop`：常驻商店直接购买（贝币/开心宝/元宝）。
- `gem_exchange`：宝石兑换（消耗特定配比的宝石兑换，共 124 种配方）。
- `crown_exchange`：皇冠兑换（消耗特定皇冠鱼兑换，共 98 种配方）。
- `event`：限时活动/节日活动获得。
- `fishing`：钓鱼达人（小游戏钓鱼玩法产出，如星座鱼）。
- `fusion`：融合系统（章鱼博士配方/限时融合）。
- `magic_summon`：魔力召唤（初级/高级水晶召唤祭坛）。
- `shell_shard`：贝壳与碎片（普通/金贝壳开贝系统及碎片合成）。
- `baby_fish`：鱼宝宝系统培育。
- `deep_sea`：深海鱼系统。
- `mission`：皇冠任务/成长任务/日常任务奖励。
- `other`：其他特定玩法系统。
- `unknown`：获取方式存在但无法归入上述类别或尚未查明。

### 3. 官方鱼类分类标签 (`category_tag`)
游戏内置 9 大官方分类标签：
- `真实鱼`、`美食鱼`、`仿物鱼`、`人型鱼`、`发光鱼`、`神秘鱼`、`系列鱼`、`鱼群`、`高级鱼群`（一条鱼可同时拥有多个标签，以空格分隔）。

> **红线**：即便标注了 `acquisition_type: ["gem_exchange"]`，也必须同时保留 `acquisition_raw: "宝石兑换"`。

### 3. 当前可用性 (`availability`)
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
