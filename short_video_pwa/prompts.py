#!/usr/bin/env python3
# -*- coding: utf-8 -*-

STYLE_GUIDES = {
    "薛辉": "情绪驱动、原生感、强钩子、晒过程、结尾反差/留悬念",
    "王泽旭": "极致聚焦、一招打透、专卖店思维、反复触达",
    "董十一": "痛点+价值+行动指令、5A路径、成交导向",
    "三把刀": "有用+有情绪、精准流量、强转化闭环",
    "金枪大叔": "强势、短句、强冲突、金句收尾",
    "婉婉的直播": "温柔松弛、共情、先留人后成交、聊天式带货",
}

PLATFORM_GUIDES = {
    "抖音": "强钩子、快节奏、强对比、少废话",
    "小红书": "清单/避坑/对比/成本，笔记感强",
    "视频号": "可信任、案例复盘、过程透明",
    "快手": "直给、口语化、结论先行",
}

SYSTEM_PROMPT = """你是短视频爆款生成器与商业内容策略师。输出必须为中文。请根据用户输入的信息，完成生意分析与内容输出，并按平台分别给出结果。必须包含：
- 生意分析
- 标题
- 钩子开头
- 脚本结构（提出问题+解决方案）
- 文案（可直接口播）
- 对标拆解（模仿点/超越点）
- 如何做得更好

要求：
1) 用用户选定的风格做表达；
2) 每个平台的语气与节奏要匹配；
3) 输出结构清晰、可复制落地；
4) 先给结论，再给过程；
5) 避免虚构数据或资质；
6) 若涉及动物采购，请强调合规检疫与交付流程。
"""


def build_user_prompt(data: dict) -> str:
    style = data.get("style")
    style_note = STYLE_GUIDES.get(style, "")
    platforms = data.get("platforms", [])
    platform_notes = "；".join([f"{p}:{PLATFORM_GUIDES.get(p,'')}" for p in platforms])

    return f"""
【输入信息】
具体生意：{data.get('business')}
行业：{data.get('industry')}
受众客户群体：{data.get('audience')}
核心卖点：{data.get('core_selling_points')}
获客方式：{data.get('acquisition_method')}
同行对标账号：{data.get('benchmarks')}
对标标题/爆款方向：{data.get('benchmark_notes')}

【风格要求】
风格：{style}（{style_note}）
平台节奏：{platform_notes}

【输出要求】
请按平台拆分输出，每个平台输出一个完整板块。每个板块包含：
1) 生意分析（简短）
2) 标题
3) 钩子开头
4) 脚本结构（提出问题+解决方案）
5) 文案（口播）
6) 对标拆解（模仿点/超越点）
7) 如何做得更好

额外要求：
- 必须强调合规交付与检疫流程（适用于动物供应行业）。
- 输出可直接用于公域引流私域成交。
""".strip()
