import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.gpt_collab import send_to_gpt, wait_for_gpt_reply

REPORT_TEXT = """【阶段执行汇报：开心水族箱 4331 Wiki 项目】

向技术指导汇报第二阶段任务推进成果与关键发现：

一、执行状态机与顶层架构加固
1. 强化确定性恢复状态机：在 3 步点击（右下宝箱 -> 第5书形按钮 -> 顶栏 Tab 6）前加入“模态退栈安全机制”（自动检测并点击左上角返回及模态叉），彻底免疫在任何次级页面/弹窗残留导致的点击错位。
2. 像素级锁定顶栏 Tab 6 精确点击坐标为 (1260, 85)。当前已通过 4331 基数、进度条、搜索框与区段导航四重强特征验证，大图鉴常驻状态为 STATE_ATLAS_READY。

二、重要突破：游戏官方本体论与分类体系完全探明
通过触发大图鉴顶栏【标签查找】（X: 1623, Y: 245），完整捕获了游戏官方策划设定的底层分类体系：
1. 官方 9 大鱼类标签（category_tag）：
   美食鱼、人型鱼、仿物鱼、鱼群、真实鱼、神秘鱼、系列鱼、高级鱼群、发光鱼。
2. 官方 10 大获取来源（acquisition_type）：
   商店（shop）、活动（event）、融合（fusion）、鱼宝宝（baby_fish）、宝石兑换（gem_exchange）、皇冠兑换（crown_exchange）、贝壳&碎片（shell_shard）、魔力召唤（magic_summon）、深海鱼（deep_sea）、其他（other）。
3. 官方存在状态过滤：数量>0、数量=0、已点亮、未点亮、已收藏。

三、实测探明 8 大“获得来源”次级跳转系统与安全返回机制
已实机勘察全部核心获取渠道的二级页面结构，并建立了确定性的安全返回坐标链路：
1. shop（商店购买）：跳转商城单鱼页，曝光了详情页隐藏字段“贝币单价”（如 500 贝币）与“饥饿时间”（如 2分钟），点击左上角 (70, 65) 无损返回；
2. gem_exchange（宝石兑换）：跳转宝石兑换系统（全游戏共 124 种鱼配方），卡片明确展示所需 6 种宝石种类与需求量（如 30/30），点击左上角 (70, 65) 无损返回；
3. crown_exchange（皇冠兑换）：跳转皇冠兑换系统（全游戏共 98 种鱼配方），明确展示所需特定“皇冠鱼”（如红橘子皇冠x2等）及附赠奖励鱼，点击左上角 (70, 65) 无损返回；
4. event（活动获得）：活动已结束时胶囊按钮呈置灰禁用态，点击无跳转，弹窗无损留存；
5. fishing（钓鱼达人）：跳转钓鱼达人大地图，点击右上角红色 [X] (1870, 70) 即可无损退出并精确回到大图鉴原滚动位置；
6. magic_summon（魔力召唤）：跳转召唤祭坛（初级 200 绿水晶 / 高级 60 粉+500 绿），点击左上角 (70, 65) 无损返回；
7. shell_shard（开贝壳）：跳转开贝壳系统（普通贝壳 / 金贝壳），点击左上角 (70, 65) 无损返回；
8. fusion（限时融合）：跳转章鱼博士新配方与熔炉（展示 3 组材料鱼复合公式），模态右上 [X] (1765, 165) + 左上 (70, 65) 无损返回。

四、第二阶段多样性异构抽样成果
1. 基于官方标签筛选体系，完成跨分类、跨渠道的精准多样性采样，正式入库有效样本增至 59 条（fish.jsonl 59 条，acquisition-methods.jsonl 59 条）。
2. 获取来源全覆盖统计：shop: 27, gem_exchange: 7, crown_exchange: 1, event: 3, fishing: 3, magic_summon: 4, fusion: 4, shell_shard: 4, baby_fish: 3, deep_sea: 3。
3. 异常处理纪律：对返回图鉴卡片渲染延迟造成的 5 次无效采样，严格按纪律剥离存入 unresolved/unresolved.jsonl，保证正式数据集 100% 清洁。
4. 全部代码、数据模型更新、工作流文档与测试工具已完整 Commit 并 Push 至 GitHub 远端仓库。

五、下一步请示与决策建议
针对后续推进路径，请指示：
【方案 A（配方深水区优先）】：由于已探明“宝石兑换”（124 配方）与“皇冠兑换”（98 配方）拥有结构化大盘，可编写专项爬虫直接一次性将这 222 种高价值确定性配方及其具体材料全部采集并沉淀入库；
【方案 B（4331 大盘扫荡优先）】：大图鉴垂直滚动单步（1 行约 290px，1 屏 12 张卡约 580px）与渲染等待（0.8s）已稳定，直接启动大图鉴分段批量采集流水线推进 4331 总体大盘。

请指导！
"""

def main():
    print("=== 发送汇报至 ChatGPT ===")
    ok = send_to_gpt(REPORT_TEXT)
    if not ok:
        print("发送汇报失败，请检查 kimi-webbridge 服务。")
        return

    reply = wait_for_gpt_reply(timeout=100)
    print("\n=== ChatGPT 最新回复 ===")
    print(reply[:500] if reply else "(暂无回复)")

    with open("logs/sessions/gpt_stage2_reply.txt", "w", encoding="utf-8") as f:
        f.write(reply or "")
    print("\n已将 ChatGPT 完整回复保存至 logs/sessions/gpt_stage2_reply.txt")

if __name__ == "__main__":
    main()
