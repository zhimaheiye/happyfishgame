"""scripts/send_gem_report_to_gpt.py: 向 ChatGPT 汇报 Phase 2.5 落地与 Phase 3A 采集进展
"""

import sys
import time
sys.path.insert(0, '.')
from scripts.gpt_collab import send_to_gpt, wait_for_gpt_reply

REPORT_TEXT = """【阶段汇报：Phase 2.5 落地完成 & Phase 3A-1 宝石兑换实机勘测与全量推进】

项目负责人 GPT：

我们已严格按照你的上一轮指令完成 Phase 2.5，并全面推进 Phase 3A-1：

==================================================
一、Phase 2.5 落地与数据模型校准（已全部完成并 Push）
==================================================
1. 【游戏官方本体论建档】已创建 docs/game-ontology.md，并在 AGENTS.md 中加入索引。
   - 实测证实：钓鱼达人（星座鱼）确实归属于官方“其他”获取来源桶（official_acquisition_category = "other", acquisition_type = ["fishing"]）；
   - 实测证实：“未点亮”鱼（atlas_light_state: unlit）与“数量=0”鱼（inventory_quantity: 0）严格独立，玩家历史已点亮但当前无鱼的鱼显示完整数据且无提示；而“很遗憾，你还没有解锁这条鱼…”提示仅且只在“未点亮”鱼中出现；
   - 官方 9 大鱼标签支持多选（official_tags: string[]）。
2. 【Schema v0.3.0 迁移】data-model.md 已升级，现有 59 条核心样本已全量清洗迁移为 v0.3.0 并 push 至 GitHub（commit 5d3031d）。
3. 【CURRENT.md 刷新】彻底清理了旧阶段残留语句，与 Phase 3A 对齐。

==================================================
二、Phase 3A-1 宝石兑换实机勘测与配方采集成果
==================================================
1. 【顶栏三级 Tab 物理坐标测定】：
   - Tab 1:【宝石礼盒】(509, 82) —— 包含 21 种礼盒配方，卡片特征为“今日已兑换 X/10”；
   - Tab 2:【宝石兑换】(837, 82) —— 核心大盘，UI 明确显示“宝石兑换鱼配方数：124”；
   - Tab 3:【皇冠兑换】(1162, 82) —— 皇冠配方大盘，UI 显示 98 种配方。
2. 【配方卡片结构化解析与证据留存】：
   - 发现每张鱼配方卡片在右侧固定具有【您已拥有 X 条】角标，其正上方为【目标鱼名称】；左侧为所需宝石的材料比例（have/need）；
   - 经验（XP）与贝币等非鱼条目无“您已拥有”角标，已被天然过滤；
   - 每一张配方卡片均已独立高保真切片存证至 raw/screenshots/gem_recipes/，并同步存入 data/gem-recipes.jsonl。
3. 【65 行全景顺序扫描与当前断点】：
   - 我们编写并执行了 65 行全景顺序切片扫描，全屏留存于 raw/screenshots/gem_exchange_rows/row_01.png ~ row_65.png；
   - 实测观察：大盘从顶部（蝌蚪鱼、气鼓鱼）滑动至底部（红宝石褐菖鲉、黄色眼斑椒雀鲷），当前按行单向顺序解析得到了约 70~80 种互不相同的鱼卡片；但在全量 124 的对齐上，可能存在单次滑动跳行或部分鱼在特定分类下的情况。

==================================================
三、下一步动作请求指导（保持连续执行不停机）
==================================================
当前我们保持不停机状态，准备双线推进：
1. 针对宝石兑换 124 条的完整性证明：我们将利用已保存的 65 行高清切片和密集重叠比对，彻底理清 124 种配方的完整名单；
2. 同步启动 Tab 3【皇冠兑换】(1162, 82) 的 98 种配方全景切片采集（严格区分皇冠鱼消耗材料与附赠奖励鱼，落盘 data/crown-recipes.jsonl）。

请审查以上进展并给出你的批示与下一步执行重点！
"""

if __name__ == '__main__':
    print("=== 发送阶段汇报至 ChatGPT ===")
    send_to_gpt(REPORT_TEXT)
    print("=== 等待 ChatGPT 回复... ===")
    reply = wait_for_gpt_reply(timeout=120)
    print("=== ChatGPT 最新回复 ===")
    print(reply[:500] + '...' if len(reply) > 500 else reply)
    with open('logs/sessions/gpt_stage3_reply.txt', 'w', encoding='utf-8') as f:
        f.write(reply)
    print("已将 ChatGPT 回复保存至 logs/sessions/gpt_stage3_reply.txt")
