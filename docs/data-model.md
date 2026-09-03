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
| `name` | `string` | **是** | - | 鱼类名称，严格依照游戏详情页标题。 |
| `category_tag` | `string \| null` | 否 | `null` | 详情页显示的类别标签（例如：“真实鱼”、“神话鱼”等）。 |
| `description` | `string \| null` | 否 | `null` | 鱼类简介/特征描述文本（如“活泼，好动”）。 |
| `produce_time_raw` | `string \| null` | 否 | `null` | 产宝时间原文（如 `"15秒"`、`"2小时"`）。**强保留**。 |
| `produce_time_seconds` | `integer \| null` | 否 | `null` | 标准化产宝周期（换算为秒）。转换失败或无法确认时填 `null`。 |
| `crown_time_raw` | `string \| null` | 否 | `null` | 皇冠时间原文（如 `"60分钟"`、`"24小时"`）。**强保留**。 |
| `crown_time_minutes` | `integer \| null` | 否 | `null` | 标准化皇冠周期（换算为分钟）。 |
| `acquisition_raw` | `string` | **是** | `""` | **核心证据字段**：游戏内显示的获取来源全部原始文字（如“商店购买”、“参加XXXX活动获得”）。 |
| `acquisition_type` | `string[]` | **是** | `[]` | 标准化获取类型列表（支持多对多），参见下方合法枚举定义。 |
| `produce_items` | `object[]` | 否 | `[]` | 产宝内容（宝物名称、产出贝币、经验数值等详情对象）。 |
| `availability` | `string` | **是** | `"unknown"` | 当前版本可获得性判定，只允许合法状态枚举。 |
| `source` | `string` | **是** | `"in_game_atlas"` | 数据源标识（游戏图鉴为 `"in_game_atlas"`）。 |
| `screenshot` | `string` | **是** | `""` | 存证全屏/详情截图相对路径（如 `"raw/screenshots/sample_01_detail.png"`）。 |
| `verified_at` | `string` | **是** | - | 采集/校验通过的 ISO-8601 时间戳（如 `"2026-09-03T18:00:00Z"`）。 |
| `notes` | `string \| null` | 否 | `null` | 采集过程中的特征补充、异常标记或特殊观察。 |

---

## 二、标准化枚举取值规范

### 1. 获取方式标准化分类 (`acquisition_type`)
获取方式采用**数组存储**以支持同一条鱼存在多种获取渠道：
- `shop`：商店直接购买（贝币/开心宝/元宝）。
- `event`：限时活动/节日活动获得。
- `exchange`：宝石兑换/图谱兑换/勋章兑换。
- `fuse`：融合/合成/孵化产出。
- `mission`：皇冠任务/成长任务/日常任务奖励。
- `other`：其他特定玩法。
- `unknown`：获取方式存在但无法归入上述类别或尚未查明。

> **红线**：即便标注了 `acquisition_type: ["shop"]`，也必须同时保留 `acquisition_raw: "商店购买"`。

### 2. 当前可用性 (`availability`)
严格限定为以下四种状态，严禁凭经验脑补：
- `current`：当前游戏内明确可以直接通过常驻手段获取。
- `unavailable`：当前明确已绝版或历史活动未返场。
- `uncertain`：无法从当前图鉴文字推断当前是否开放（例如标明了活动名称，但不确定该活动目前是否在运行）。
- `unknown`：缺乏任何获取渠道信息。

---

## 三、待处理队列：`unresolved/unresolved.jsonl`

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

## 四、Schema 演化记录 (Changelog)

### 2026-09-03 · v0.1.0 初始骨架定义
- **起因**：项目启动，根据小丑鱼等初始图鉴详情样本，定义首版数据字段。
- **改动**：
  1. 确立 `acquisition_raw` 与 `acquisition_type` 彻底解耦；
  2. 确立 `availability` 严谨四值约束；
  3. 确立 `screenshot` 作为不可缺失的证据链锚点。
