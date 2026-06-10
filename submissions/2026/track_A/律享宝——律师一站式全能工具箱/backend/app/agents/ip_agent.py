"""
律师 IP 智能运营 Agent（P1）
基于 Google Gemma 4 内容生成与多格式适配能力，实现律师个人 IP 从包装到分发的全流程自动化
"""
from app.agents.gemma4_client import gemma_client

SYSTEM_PROMPT = """你是一名资深律师品牌运营专家，精通律师个人 IP 打造和新媒体运营。
你的任务是根据律师个人信息，生成合规、专业的个人品牌宣传内容。

工作流程：
1. 审核并脱敏用户输入的个人信息
2. 美化润色个人简介、擅长领域、成功案例
3. 生成适配不同平台的宣传素材（文案、海报文字、短视频脚本）
4. 规划个性化内容发布策略

核心要求：
- 所有内容必须符合律师执业规范，禁止虚假宣传
- 案例必须经过脱敏处理（隐去当事人姓名、身份证号、手机号、具体金额）
- 语言专业但不晦涩，突出律师专业能力和信任感
- 输出格式为结构化 JSON"""

# 平台与素材类型
PLATFORMS = [
    {"name": "微信朋友圈", "format": "短文案+海报", "max_length": 200},
    {"name": "小红书", "format": "笔记文案+配图", "max_length": 1000},
    {"name": "抖音/视频号", "format": "口播脚本+字幕", "max_length": 1500},
    {"name": "知乎", "format": "专业长文", "max_length": 5000},
    {"name": "私域社群", "format": "成交型文案", "max_length": 500},
]

# 信任背书模块文案类型
TRUST_CONTENT_TYPES = [
    "个人独立执业优势（去大所依附）",
    "办案合规安全保障说明",
    "客户资金安全、无平台牵连风险说明",
]


def desensitize(text: str) -> str:
    """
    对个人信息进行脱敏处理
    """
    import re
    # 脱敏手机号
    text = re.sub(r'1[3-9]\d{9}', lambda m: m.group()[:3] + '****' + m.group()[-4:], text)
    # 脱敏身份证号
    text = re.sub(r'\d{17}[\dXx]', lambda m: m.group()[:6] + '********' + m.group()[-4:], text)
    # 脱敏具体金额（保留数字但去掉精确值）
    text = re.sub(r'(金额|人民币|¥|￥)\s*[\d,]+\.?\d*', lambda m: m.group(0).split('\\d')[0] + '**元', text)
    return text


def generate_profile(lawyer_info: dict) -> dict:
    """
    生成律师个人简介、擅长领域包装
    """
    user_input = f"""请根据以下律师信息生成专业包装内容：

姓名：{lawyer_info.get('name', '')}
执业年限：{lawyer_info.get('practice_years', '')}
学历：{lawyer_info.get('education', '')}
资质/荣誉：{lawyer_info.get('qualifications', '未提供')}
擅长领域：{lawyer_info.get('specialties', '')}
执业机构：{lawyer_info.get('firm', '未提供')}
个人简介（原始）：{lawyer_info.get('bio', '未提供')}
"""

    output_schema = {
        "type": "object",
        "properties": {
            "professional_title": {"type": "string", "description": "专业头衔（一句话定位）"},
            "polished_bio": {"type": "string", "description": "润色后的个人简介（200字以内）"},
            "specialties_display": {"type": "array", "items": {"type": "string"}, "description": "擅长领域列表（美化后）"},
            "achievement_highlights": {"type": "array", "items": {"type": "string"}, "description": "成就亮点列表"},
            "personal_tagline": {"type": "string", "description": "个人标语/签名"},
        },
        "required": ["professional_title", "polished_bio"],
    }

    result = gemma_client.generate_structured(SYSTEM_PROMPT, user_input, output_schema)
    return {
        "lawyer_name": lawyer_info.get("name", ""),
        "professional_title": result["parsed"].get("professional_title", ""),
        "polished_bio": result["parsed"].get("polished_bio", ""),
        "specialties_display": result["parsed"].get("specialties_display", []),
        "achievement_highlights": result["parsed"].get("achievement_highlights", []),
        "personal_tagline": result["parsed"].get("personal_tagline", ""),
        "tokens_used": result["tokens_used"],
    }


def generate_case_description(case_info: dict) -> dict:
    """
    生成合规脱敏后的成功案例描述
    """
    raw_text = f"""案例类型：{case_info.get('case_type', '')}
案件结果：{case_info.get('result', '')}
客户评价：{case_info.get('client_feedback', '未提供')}
涉及人物：{case_info.get('parties', '')}
"""

    # 脱敏
    safe_text = desensitize(raw_text)

    user_input = f"""请将以下成功案例加工成合规的宣传文案（已做脱敏处理）：

{safe_text}

要求：
1. 隐去所有可识别当事人身份的信息
2. 突出律师的专业能力和案件成果
3. 控制在300字以内
4. 适合用于律师个人网站、社交媒体等宣传渠道"""

    output_schema = {
        "type": "object",
        "properties": {
            "case_title": {"type": "string", "description": "案例标题"},
            "case_description": {"type": "string", "description": "案例描述（合规版）"},
            "key_points": {"type": "array", "items": {"type": "string"}, "description": "本案凸显的律师能力点"},
            "applicable_platforms": {"type": "array", "items": {"type": "string"}, "description": "适合发布的平台"},
        },
        "required": ["case_title", "case_description"],
    }

    result = gemma_client.generate_structured(SYSTEM_PROMPT, user_input, output_schema)
    return {
        "case_title": result["parsed"].get("case_title", ""),
        "case_description": result["parsed"].get("case_description", ""),
        "key_points": result["parsed"].get("key_points", []),
        "applicable_platforms": result["parsed"].get("applicable_platforms", []),
        "tokens_used": result["tokens_used"],
    }


def generate_platform_material(lawyer_info: dict, platform: str, material_type: str = "auto") -> dict:
    """
    生成指定平台的宣传素材
    """
    name = lawyer_info.get("name", "律师")
    specialties = lawyer_info.get("specialties", "")

    user_input = f"""律师姓名：{name}
擅长领域：{specialties}
目标平台：{platform}
素材类型：{material_type}

请为这位律师生成适合在"{platform}"发布的宣传素材。"""

    platform_note = ""
    for p in PLATFORMS:
        if p["name"] == platform:
            platform_note = f"（格式要求：{p['format']}，建议不超过{p['max_length']}字）"
            break

    prompt = SYSTEM_PROMPT + f"""
针对{platform}{platform_note}，请生成以下内容（JSON格式）：
1. 标题/文案
2. 正文内容
3. 建议配图说明（如有）
4. 适合的话题标签（如有）"""

    output_schema = {
        "type": "object",
        "properties": {
            "platform": {"type": "string"},
            "title": {"type": "string", "description": "标题/文案标题"},
            "content": {"type": "string", "description": "正文内容"},
            "image_description": {"type": "string", "description": "建议配图描述"},
            "hashtags": {"type": "array", "items": {"type": "string"}, "description": "话题标签"},
            "publish_tips": {"type": "string", "description": "发布建议/注意事项"},
        },
        "required": ["platform", "title", "content"],
    }

    result = gemma_client.generate_structured(prompt, user_input, output_schema)
    return {
        "platform": platform,
        "title": result["parsed"].get("title", ""),
        "content": result["parsed"].get("content", ""),
        "image_description": result["parsed"].get("image_description", ""),
        "hashtags": result["parsed"].get("hashtags", []),
        "publish_tips": result["parsed"].get("publish_tips", ""),
        "tokens_used": result["tokens_used"],
    }


def generate_trust_content(lawyer_info: dict, content_type: str) -> dict:
    """
    生成信任背书文案
    """
    user_input = f"""律师姓名：{lawyer_info.get('name', '')}
执业年限：{lawyer_info.get('practice_years', '')}
擅长领域：{lawyer_info.get('specialties', '')}
内容类型：{content_type}

请生成一份针对潜在客户的信任背书文案。"""

    prompt = SYSTEM_PROMPT + f"""
内容类型：{content_type}

要求：
- 语气真诚、专业
- 直击客户当前最关心的痛点
- 提供具体的解决方案说明
- 200字以内"""

    result = gemma_client.generate(prompt, user_input)
    return {
        "content_type": content_type,
        "content": result["content"],
        "tokens_used": result["tokens_used"],
    }


def generate_publish_strategy(lawyer_info: dict) -> dict:
    """
    生成个性化的内容发布策略
    """
    user_input = f"""律师姓名：{lawyer_info.get('name', '')}
执业年限：{lawyer_info.get('practice_years', '')}
擅长领域：{lawyer_info.get('specialties', '')}
目标客户：{lawyer_info.get('target_clients', '未提供')}

请制定一份为期一周的内容发布策略规划。"""

    prompt = SYSTEM_PROMPT + """
请输出一份完整的内容发布策略，包括：
1. 周发布节奏建议（周几发什么）
2. 各平台内容方向建议
3. 互动与转化策略
4. 关键词/话题建议"""
    
    result = gemma_client.generate(prompt, user_input)

    return {
        "strategy": result["content"],
        "tokens_used": result["tokens_used"],
    }
