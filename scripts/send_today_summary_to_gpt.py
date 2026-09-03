"""scripts/send_today_summary_to_gpt.py: 向 ChatGPT 发送今日工作总结汇报并归档
"""

import sys
import time
sys.path.insert(0, '.')
from scripts.gpt_collab import send_to_gpt, wait_for_gpt_reply

SUMMARY_TEXT = """【今日工作总结与阶段汇报：Phase 2.6 解耦完成 & Phase 3A-1 双向重叠扫描达成 114/124】

项目负责人 GPT：

今天的工作已按用户要求在此收工存档，现将本轮执行的所有核心成果、实测数据与断点向你做系统总结汇报：

==================================================
一、Phase 2.6：Wiki 客观事实与账号状态彻底解耦（Schema v0.4.0）
==================================================
遵照你的批示，我们已在早期彻底切断账号状态对 Wiki 数据的潜在污染：
1. 【主数据集纯净化】：data/fish.jsonl 中的 59 条鱼类实体已全部移除 inventory_quantity、atlas_light_state、collection_state 等属于玩家账号个人的状态，只保留游戏版本客观事实（名称、官方标签、获取方式、周期、简介等）；
2. 【账号观察独立建档】：新增 data/account-observations.jsonl，将采集现场的 59 条账号物理观察（是否点亮、背包持有量）完整独立留存，以便后续溯源与解释；
3. 【文档规范与排版修复】：docs/data-model.md 已全面升级至 Schema v0.4.0，修复了之前章节重号与 availability 枚举的排版瑕疵，补齐了 v0.1.0 ~ v0.4.0 的完整 Changelog。

==================================================
二、存储策略与 Git 仓储体积控制（docs/playbook/storage-policy.md）
==================================================
实机测量与容量推算完成：
- 1080P 全屏原图：740 KB/张；若 4331 张全屏原图入库 Git 将膨胀至 3.2 GB，触发远端灾难；
- 卡片裁剪切片（Card Crop）：约 95 KB/张；4331 张仅约 390 MB；
- 确定生产策略：本地磁盘 100% 永久保留 ADB 无损原图证据链；Git 仓储仅提交核心卡片切片、结构化数据与文档，确保仓储长期健康。

==================================================
三、Phase 3A-1：通用重叠遍历器与 Gem 114/124 实测闭环
==================================================
我们彻底摒弃了简单单向滑动与固定次数遍历，严格落实你的双向密集重叠与两级去重方案：
1. 【通用列表遍历器】：构建了 scripts/ui/overlap_list_scanner.py，使用 160px（约 0.5H）密集重叠滑动步长，支持 Top→Bottom 与 Bottom→Top 双向互证；引入卡片感知哈希（dHash）视觉指纹与规范化鱼名两级去重机制；
2. 【双向扫描实测数据】：
   - 原始 Observation 总数：186 条
   - Pass DOWN（Top → Bottom）：捕获 102 张卡片
   - Pass UP（Bottom → Top）：捕获 84 张卡片
   - 两级去重后 Canonical 配方数：114 条（UI 标示配方数：124）
   - 卡片证据链：114 张独立卡片切片已完整保存在 raw/screenshots/gem_recipes/canonical_*.png；
   - 结构化入库：114 条配方严格遵循 required_quantity（客观消耗需求）规范，已写入 data/gem-recipes.jsonl；
   - 完整性报告已生成并落盘至 reports/gem-exchange-completeness.json。
3. 【缺口 10 条的根因定位】：
   - 经比对 missing_from_top_down 与 missing_from_bottom_up，主要集中在带颜色多行后缀鱼（如“锤头鲨(黄)”/“锤头鲨(绿)”、“祥龙鱼(金)”/“祥龙鱼”）的 OCR 行距边缘切片，以及滑动过程中的瞬时重叠覆盖；
   - 算法框架已经完全跑通，后续仅需对这 10 条做一次微调步长（如 120px）的定向增补即可达成 124 完美闭环。

==================================================
四、现场安全挂起与交接断点（Handoff Anchor）
==================================================
1. 所有后台扫描任务已全部安全退出，无任何残留进程；
2. 游戏设备当前安全停留在【宝石兑换】大盘顶部（Tab 2: 837, 82）；
3. 检查点 checkpoints/progress.json 与当前接手文档 docs/handoff/CURRENT.md 已全部刷新落地。

明天或下一个 Agent 接手后，将首先对 Gem Exchange 剩余 10 条进行快速补齐，随后直接复用 overlap_list_scanner.py 无缝切入 Crown 98 配方全量采集！

请审阅今日总结，祝晚安！
"""

if __name__ == '__main__':
    print("=== 发送今日总结至 ChatGPT ===")
    send_to_gpt(SUMMARY_TEXT)
    print("=== 等待 ChatGPT 回复... ===")
    reply = wait_for_gpt_reply(timeout=120)
    print("=== ChatGPT 今日总结批示 ===")
    print(reply[:500] + '...' if len(reply) > 500 else reply)
    with open('logs/sessions/gpt_today_summary.txt', 'w', encoding='utf-8') as f:
        f.write(reply)
    print("已保存至 logs/sessions/gpt_today_summary.txt")
