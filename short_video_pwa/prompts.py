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

# ─── Module 0: 爆款文案生成器 ────────────────────────────────────────────────

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


# ─── Module 1: 带货视频生成器 ─────────────────────────────────────────────────

PRODUCT_VIDEO_SYSTEM_PROMPT = """你是顶级电商短视频策划专家与带货脚本大师。输出必须为中文。
你的任务是：根据用户上传的商品图片与描述，深度分析商品卖点，生成完整的带货短视频制作方案。

输出必须包含以下所有板块：
1. 【商品卖点分析】：从图片与描述中提炼3-5个核心卖点，每个卖点附上"用户痛点→产品解决方案"的对应说明
2. 【带货脚本】：完整口播文案，包含钩子开场、卖点展示、促单话术、行动指令（≥300字）
3. 【数字人拍摄指令】：告诉数字人如何展示商品，包括动作、表情、镜头切换节奏（适合HeyGen/D-ID等工具直接使用）
4. 【场景与服装建议】：数字人的背景场景、服装、道具建议，确保与商品调性匹配
5. 【是否为服装商品】：若是服装类，额外输出"虚拟试穿方案"，描述数字人如何展示穿搭效果
6. 【视频节奏规划】：按时间轴（0-3s / 3-8s / 8-15s / 15-30s / 30s+）规划每段内容
7. 【平台发布建议】：针对抖音/小红书/视频号分别给出标题、话题标签、最佳发布时段

风格要求：专业、有感染力、以成交为导向，避免夸大宣传。
"""


def build_product_video_prompt(data: dict, has_image: bool = False) -> str:
    category = data.get("category", "通用商品")
    description = data.get("description", "")
    target_audience = data.get("target_audience", "")
    price_range = data.get("price_range", "")
    digital_human_desc = data.get("digital_human_desc", "")
    style = data.get("style", "")
    platforms = data.get("platforms", [])

    is_clothing = any(kw in category for kw in ["服装", "衣服", "穿搭", "上衣", "裤子", "裙子", "外套", "T恤"])
    clothing_note = (
        "- 该商品为服装类，请重点输出虚拟试穿方案，描述数字人穿上该服装后如何展示穿搭效果、搭配建议及上身效果。\n"
        if is_clothing else ""
    )

    image_note = "（用户已上传商品图片，请结合图片进行分析）" if has_image else "（用户未上传图片，请根据文字描述进行分析）"

    return f"""
【商品信息】
商品类目：{category} {image_note}
商品描述：{description}
目标受众：{target_audience}
价格区间：{price_range}
是否为服装类：{"是" if is_clothing else "否"}

【数字人信息】
数字人描述：{digital_human_desc}（形象风格、性别、气质等）

【内容要求】
表达风格：{style or "专业亲和、成交导向"}
发布平台：{", ".join(platforms) if platforms else "抖音、小红书"}

【特别说明】
{clothing_note}- 脚本须包含完整的成交闭环：引流→留存→种草→促单。
- 数字人拍摄指令须足够具体，可直接输入HeyGen、D-ID、硅基智能等工具。
""".strip()


# ─── Module 2: 口播脚本生成器 ─────────────────────────────────────────────────

VOICEOVER_SYSTEM_PROMPT = """你是顶级短视频内容策略师与口播脚本改写专家。输出必须为中文。
你的任务是：分析用户提供的对标账号视频信息，提炼爆款规律，改写出属于用户自己的原创口播脚本，并给出完整的数字人视频制作方案。

输出必须包含以下所有板块：
1. 【对标视频拆解】：分析对标视频的选题逻辑、钩子策略、内容结构、情绪节奏、成交方式
2. 【爆款规律总结】：提炼2-3条可复用的爆款公式（格式：公式名称 + 使用场景 + 效果预期）
3. 【原创改写脚本】：完整口播脚本，保留对标视频的爆款结构，但内容、角度、案例全部原创化（≥400字）
4. 【钩子升级方案】：在对标视频钩子基础上，提供3个更强的开头变体
5. 【数字人拍摄指令】：告诉数字人如何呈现该口播脚本，包括语速、停顿、表情、手势、镜头建议
6. 【场景模仿超越方案】：参考对标视频场景，给出"模仿点"与"超越点"，包括背景、道具、灯光建议
7. 【多平台适配版本】：针对抖音/小红书/视频号，分别调整语气与节奏，输出适配版脚本要点
8. 【发布策略建议】：标题、话题、发布时间、互动引导话术

风格要求：原创性强、节奏感好、情绪充沛，绝对不抄袭原视频文案。
"""


def build_voiceover_prompt(data: dict) -> str:
    video_url = data.get("video_url", "")
    video_topic = data.get("video_topic", "")
    video_description = data.get("video_description", "")
    own_business = data.get("own_business", "")
    own_audience = data.get("own_audience", "")
    digital_human_desc = data.get("digital_human_desc", "")
    style = data.get("style", "")
    platforms = data.get("platforms", [])

    return f"""
【对标视频信息】
视频链接：{video_url or "（未提供链接）"}
视频主题/选题：{video_topic}
视频内容描述：{video_description}
（注：若无法访问链接，请根据主题和描述进行分析改写）

【我的账号信息】
我的业务/领域：{own_business}
我的目标受众：{own_audience}

【数字人信息】
数字人描述：{digital_human_desc}

【内容要求】
表达风格：{style or "专业、有感染力、原创性强"}
发布平台：{", ".join(platforms) if platforms else "抖音、小红书"}

【特别说明】
- 改写后的脚本必须完全原创，不能与原视频文案相同。
- 在保留爆款结构的基础上，内容要更贴合我的业务与受众。
- 数字人拍摄指令需足够具体，可直接输入HeyGen、D-ID、硅基智能等工具。
- 场景设计需参考对标视频风格，但要在细节上有所超越。
""".strip()


# ─── Module 3: 多平台一键发布 ─────────────────────────────────────────────────

PUBLISH_SYSTEM_PROMPT = """你是多平台短视频运营专家与内容分发策略师。输出必须为中文。
你的任务是：根据用户的视频内容，为每个目标平台生成最优的发布方案，帮助用户实现最大化流量与转化。

输出必须包含以下所有板块：
1. 【视频内容分析】：简要分析视频的核心价值点、目标人群、传播潜力
2. 【各平台发布方案】：针对每个选定平台，分别输出：
   - 标题（≥3个备选，含数字/悬念/痛点等钩子策略）
   - 正文文案（符合平台调性，含话题标签）
   - 话题标签（10-15个，含热门话题+精准长尾话题）
   - 封面文字建议
   - 最佳发布时段（具体到几点）
   - 互动引导话术（评论区置顶用）
3. 【跨平台差异化策略】：说明各平台的差异化定位，避免内容同质化
4. 【数据追踪建议】：发布后应重点监控哪些指标，以及如何根据数据优化
5. 【追更/系列化建议】：该视频是否适合做成系列，若适合给出后续选题建议

注意：标题和文案要真实可信，不虚构数据，不使用极限词，符合各平台内容审核规范。
"""


def build_publish_prompt(data: dict) -> str:
    video_title = data.get("video_title", "")
    video_description = data.get("video_description", "")
    video_category = data.get("video_category", "")
    core_selling_points = data.get("core_selling_points", "")
    target_audience = data.get("target_audience", "")
    platforms = data.get("platforms", [])
    account_style = data.get("account_style", "")

    return f"""
【视频信息】
视频标题/主题：{video_title}
视频内容摘要：{video_description}
内容类目：{video_category}
核心价值点/卖点：{core_selling_points}
目标受众：{target_audience}

【账号信息】
账号风格定位：{account_style or "未说明"}

【发布平台】
{", ".join(platforms) if platforms else "抖音、小红书、视频号"}

【输出要求】
- 每个平台单独一个完整板块，内容针对该平台特性量身定制。
- 标题必须有吸引力，建议3个备选。
- 话题标签需结合热门话题与精准垂直话题。
- 文案符合平台审核规范，不使用违禁词。
- 互动话术要自然，能引导用户评论和转发。
""".strip()
