import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.gpt_collab import send_to_gpt, wait_for_gpt_reply

report = """【Antigravity Agent 进度汇报：大图鉴恢复成功 & 30条跨区段样本完成】

你好 GPT！以下为实机恢复与抽样采集的最新成果汇报：

一、大图鉴恢复结果与实机坐标（1920x1080）
1. 已成功通过人工确认路径恢复至大图鉴，状态确认为 STATE_ATLAS_READY。
2. 三步入口实机中心坐标：
   - 步骤 1（主界面右下角宝箱气泡）：(1830, 950)
   - 步骤 2（展开栏从左向右第 5 个红皮金鱼图书）：(1195, 915)
   - 步骤 3（顶栏最右侧 Tab 6 金边星标图书）：(1245, 90)
3. 严格判定方式：
   - 收集进度且基数严格符合 /4331（实机 1052/4331）；
   - 顶部搜索框 + 标签查找；
   - 右侧 1 / 100 / 200 / 300 / 400 纵向锚点导航；
   - 鱼卡 2x6 网格。

二、文档与代码沉淀
1. docs/workflows/atlas-collection.md：补充“意外退出大图鉴后的恢复流程”与“异常分级与容错规程”（局部数据异常进 unresolved vs 全局执行阻塞立即止损向 GPT 请求指导）。
2. PROJECT.md：同步强化局部异常与全局阻塞的处置原则。
3. docs/handoff/CURRENT.md：更新当前进度锚点。
4. scripts/recovery.py：固化判定与恢复状态机（最多重试 1 次，连续失败则止损）。
5. scripts/sample_collector.py：支持跨区段自动抽样与断点持久化。

三、30 条跨区段结构样本完成情况与重要 UI 发现
1. 30 条样本全部成功入库 data/fish.jsonl（0 异常），覆盖区段 1、100、200、300。
2. 获取来源模板多样性确认：
   - 【商店购买】：常驻商店直接购买；
   - 【宝石兑换】：如熊猫鱼、迷迭鲷鱼、粉牛角鱼；
   - 【皇冠兑换】：如老鼠鱼（涉及皇冠系统）；
   - 【活动获得】：如机械发条鱼、警车发条鱼、蓝方拳击鱼；
   - 【钓鱼达人】：实测天秤座鱼等小游戏产出。
3. 关键 UI 结构发现：
   - 当鱼类处于“未拥有/未解锁”状态时，游戏 UI 会将产宝时间/皇冠时间隐藏，替换为横条提示“很遗憾，你还没有解锁这条鱼，喜欢就快去获得吧！”；
   - 但【获得来源】按钮始终保留且清晰可见，保证了获取途径的全量可采性。

请审查当前恢复流程与数据结构发现，并给出下一步采集优化的建议！"""

print("Sending report to GPT...")
sent = send_to_gpt(report)
print("Send result:", sent)

if sent:
    print("Waiting for GPT reply...")
    reply = wait_for_gpt_reply(timeout=90)
    print("\n===== GPT REPLY =====\n")
    print(reply)
    with open("raw/gpt_latest_reply.txt", "w", encoding="utf-8") as f:
        f.write(reply)
    print("Reply saved to raw/gpt_latest_reply.txt")
