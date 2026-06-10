"""
律享宝首页导航数据 — 来自 PRD 完整版
12 大分类 + 27 个工具（含 Logo 直链、官网、教程）
"""
# ===== 12 大分类 =====
CATEGORIES = [
    {"id": 1, "name": "法律智能检索", "icon": "Search"},
    {"id": 2, "name": "合同智能审查", "icon": "DocumentChecked"},
    {"id": 3, "name": "案件/合同管理", "icon": "List"},
    {"id": 4, "name": "视听证据整理", "icon": "Microphone"},
    {"id": 5, "name": "模拟法庭实训", "icon": "ScaleOfJustice"},
    {"id": 6, "name": "法律文书写作", "icon": "EditPen"},
    {"id": 7, "name": "多场景法律翻译", "icon": "ChatLineSquare"},
    {"id": 8, "name": "法律长材料精读阅读", "icon": "Reading"},
    {"id": 9, "name": "司法公文撰写", "icon": "Notebook"},
    {"id": 10, "name": "律师知识管理", "icon": "FolderOpened"},
    {"id": 11, "name": "案情文本可视化", "icon": "DataLine"},
    {"id": 12, "name": "多端协同办公", "icon": "Connection"},
]

# ===== 27 个工具明细 =====
TOOLS = [
    # 1. 法律智能检索
    {
        "id": 1, "category_id": 1, "name": "秘塔 AI 搜索",
        "logo_url": "/logos/秘塔 AI 搜索.png",
        "official_url": "https://metaso.cn",
        "description": "专业法律类智能检索，查判例、裁判思路首选",
        "tutorial": "打开页面直接输入案由、法条、案件争议点即可检索\n支持自然语言提问办案思路、同类案件胜诉经验\n自动整合裁判文书、法官观点、实务办案经验\n外勤办案、庭前预判裁判倾向高效使用",
        "is_hot": True, "sort_order": 1,
    },
    {
        "id": 2, "category_id": 1, "name": "微信 AI 搜索",
        "logo_url": "/logos/微信 AI 搜索.png",
        "official_url": "https://weixin.sogou.com",
        "description": "移动端轻量化法律资讯、新规快速查询",
        "tutorial": "微信顶部搜索框开启 AI 智能搜索功能\n语音输入快速查找司法新规、地方指导案例\n无需电脑，开庭途中随时核对法条与裁判观点\n适合碎片化快速查阅法律资讯",
        "is_hot": False, "sort_order": 2,
    },
    # 2. 合同智能审查
    {
        "id": 3, "category_id": 2, "name": "法天使 - 案牍",
        "logo_url": "/logos/法天使.png",
        "official_url": "https://www.fatianshi.cn",
        "description": "律师专用 AI 合同风险审查、条款优化平台",
        "tutorial": "粘贴合同全文或上传 Word、PDF 合同文件\nAI 自动识别合同类型，标注权责漏洞、违约风险、无效条款\n一键补齐缺失必备法律条款，生成合规修订版本\n适用于买卖、劳务、工程、借贷、股权各类商事合同",
        "is_hot": True, "sort_order": 3,
    },
    # 3. 案件/合同管理
    {
        "id": 4, "category_id": 3, "name": "飞书多维表格",
        "logo_url": "/logos/飞书.png",
        "official_url": "https://www.feishu.cn",
        "description": "律所案件台账、时效提醒、团队协同管理",
        "tutorial": "新建表格搭建律师专属案件管理模板\n录入案号、当事人、开庭时间、上诉期限、审限节点\n设置智能时效提醒，避免错过递交、上诉期限\n律所团队多人在线协同统一管理全部在办案件",
        "is_hot": False, "sort_order": 4,
    },
    # 4. 视听证据整理
    {
        "id": 5, "category_id": 4, "name": "通义听悟",
        "logo_url": "/logos/通义听悟.png",
        "official_url": "https://tingwu.aliyun.com",
        "description": "庭审/会见/谈话录音极速转文字整理证据",
        "tutorial": "上传各类现场录音文件，支持长时长音频\n自动区分不同说话人，精准拆分对话内容\n智能提炼自认事实、关键争议、庭审重点表述\n快速生成会见笔录、庭审摘录、书面证据材料",
        "is_hot": True, "sort_order": 5,
    },
    # 5. 模拟法庭实训
    {
        "id": 6, "category_id": 5, "name": "北大法宝模拟法庭",
        "logo_url": "https://www.pkulaw.com/favicon.ico",
        "official_url": "https://www.pkulaw.com/moot",
        "description": "青年律师庭审辩论、质证实战训练平台",
        "tutorial": "选择民事、刑事、行政对应案由进入模拟场景\n自主扮演代理人、辩护人完成完整庭审流程\n系统实时纠正法条错误、辩论逻辑漏洞\n快速提升开庭表达、临场应变与质证能力",
        "is_hot": False, "sort_order": 6,
    },
    # 6. 法律文书写作
    {
        "id": 7, "category_id": 6, "name": "AlphaGPT 法律 AI",
        "logo_url": "https://alphalawyer.cn/favicon.ico",
        "official_url": "https://alphalawyer.cn",
        "description": "垂直法律专用 AI，一键生成法院标准文书",
        "tutorial": "选择起诉状、答辩状、上诉状、代理词、辩护词等品类\n填写基础案情、当事人信息、核心争议即可生成\n自动适配全国法院通用排版格式\n民事、商事、婚姻家事、劳动纠纷全覆盖使用",
        "is_hot": True, "sort_order": 7,
    },
    # 7. 多场景法律翻译
    {
        "id": 8, "category_id": 7, "name": "智谱清言",
        "logo_url": "/logos/智谱清言.png",
        "official_url": "https://www.zhipuai.cn",
        "description": "长文本涉外法律文书专业翻译",
        "tutorial": "粘贴外文判决书、涉外协议、境外法条文本\n切换法律专业翻译语境，精准匹配司法专业术语\n保留原文条文逻辑结构，适合跨境法律业务使用",
        "is_hot": False, "sort_order": 8,
    },
    {
        "id": 9, "category_id": 7, "name": "腾讯会议",
        "logo_url": "https://meeting.tencent.com/favicon.ico",
        "official_url": "https://meeting.tencent.com",
        "description": "涉外线上沟通实时双语翻译转写",
        "tutorial": "开启会议实时字幕与多国语言翻译功能\n涉外调解、跨境法律咨询、远程谈判实时互译\n自动留存双语文字记录，留存沟通凭证",
        "is_hot": False, "sort_order": 9,
    },
    {
        "id": 10, "category_id": 7, "name": "沉浸式翻译",
        "logo_url": "/logos/沉浸式翻译.svg",
        "official_url": "https://immersivetranslate.com",
        "description": "浏览器插件双语对照翻译外文法律网站",
        "tutorial": "安装浏览器插件后一键启用\n打开境外判例网站、外文法条页面自动双语对照\n不破坏原网页排版，无障碍查阅海外法律资料",
        "is_hot": False, "sort_order": 10,
    },
    {
        "id": 11, "category_id": 7, "name": "DeepL",
        "logo_url": "/logos/DeepL.svg",
        "official_url": "https://www.deepl.com",
        "description": "高精度正式法律书面翻译",
        "tutorial": "优先用于涉外合同、仲裁文书、正式法务函件\n译文严谨正式，规避口语化错误\n涉外律师对外正式文书翻译首选工具",
        "is_hot": False, "sort_order": 11,
    },
    # 8. 法律长材料精读阅读
    {
        "id": 12, "category_id": 8, "name": "豆包 AI 阅读",
        "logo_url": "/logos/豆包 AI 阅读.png",
        "official_url": "https://www.doubao.com",
        "description": "卷宗、判决书、长案卷快速提炼梳理",
        "tutorial": "挂载长篇判决书、全套案件卷宗、审计报告\nAI 自动浓缩案情摘要、梳理案件时间线\n快速抓取案件胜诉点、风险点与上诉核心理由",
        "is_hot": True, "sort_order": 12,
    },
    # 9. 司法公文撰写
    {
        "id": 13, "category_id": 9, "name": "DeepSeek",
        "logo_url": "https://www.deepseek.com/favicon.ico",
        "official_url": "https://www.deepseek.com",
        "description": "长篇司法分析、办案总结、调研报告撰写",
        "tutorial": "适合撰写案件研判报告、办案工作总结、法治调研文稿\n自动梳理行文框架，逻辑层次清晰严谨\n文风正式规整，适配律所内部汇报材料",
        "is_hot": True, "sort_order": 13,
    },
    {
        "id": 14, "category_id": 9, "name": "新华妙笔",
        "logo_url": "/logos/新华妙笔.png",
        "official_url": "https://miaobi.xinhuaskl.com/",
        "description": "官方标准法治宣传、政务公文创作",
        "tutorial": "撰写普法文案、法治宣传稿、行业汇报材料\n用词规范权威，贴合官方公文行文风格\n适合律所对外宣传、政务对接文稿使用",
        "is_hot": False, "sort_order": 14,
    },
    {
        "id": 15, "category_id": 9, "name": "WPS AI",
        "logo_url": "/logos/WPSAI.png",
        "official_url": "https://ai.wps.cn",
        "description": "律师函、催告函快速写作 + 统一文书排版",
        "tutorial": "在 WPS 文档内唤起 AI 助手快速生成各类公务文书\n一键统一法院标准字体、行距、页面版式\n批量润色法律文稿，精简优化专业表述",
        "is_hot": False, "sort_order": 15,
    },
    # 10. 律师知识管理
    {
        "id": 16, "category_id": 10, "name": "Get 笔记",
        "logo_url": "https://getnote.app/favicon.ico",
        "official_url": "https://getnote.app",
        "description": "个人办案模板、实务经验知识库沉淀",
        "tutorial": "分类收纳文书模板、庭审话术、办案实务心得\n关键词全局检索，快速调取同类案件办案经验\n长期搭建专属个人律师实务资源库",
        "is_hot": False, "sort_order": 16,
    },
    {
        "id": 17, "category_id": 10, "name": "ima",
        "logo_url": "https://www.ima.ai/favicon.ico",
        "official_url": "https://www.ima.ai",
        "description": "轻量化云端随手办案记录工具",
        "tutorial": "开庭、会见、外勤随时快速记录办案要点\n支持图文混合存档，多端数据实时同步\n碎片化整理日常办案灵感与实务要点",
        "is_hot": False, "sort_order": 17,
    },
    {
        "id": 18, "category_id": 10, "name": "律 AI 多",
        "logo_url": "https://p3-flow-imagex-sign.byteimg.com/tos-cn-i-a9rns2rl98/opensearch_logo_law.png",
        "official_url": "内部专属法律 AI 入口",
        "description": "法律行业垂直专用 AI 实务工具",
        "tutorial": "内置海量律师专用答辩思路、办案话术、实务模板\n垂直法律场景适配度更高，贴合一线办案需求\n快速生成行业专属法律实务内容",
        "is_hot": False, "sort_order": 18,
    },
    # 11. 案情文本可视化
    {
        "id": 19, "category_id": 11, "name": "Mermaid",
        "logo_url": "https://mermaid.live/favicon.ico",
        "official_url": "https://mermaid.live",
        "description": "一键生成案情关系图、资金流向、时间线图表",
        "tutorial": "输入简易文字指令即可自动生成专业可视化图表\n快速制作人物关系图、资金流转图、案件时间轴\n用于庭审可视化举证、律所案情分析汇报材料",
        "is_hot": False, "sort_order": 19,
    },
    # 12. 多端协同办公
    {
        "id": 20, "category_id": 12, "name": "微信 AI 输入法",
        "logo_url": "https://pinyin.weixin.qq.com/favicon.ico",
        "official_url": "https://pinyin.weixin.qq.com",
        "description": "语音速记、法律术语智能补全",
        "tutorial": "手机电脑双端同步法律专业词库\n语音口述快速记录会见内容、外勤取证笔录\nAI 自动补全法律固定句式，大幅提升文书录入效率",
        "is_hot": False, "sort_order": 20,
    },
]

# 构建按分类分组的便捷索引
TOOLS_BY_CATEGORY = {}
for t in TOOLS:
    cid = t["category_id"]
    TOOLS_BY_CATEGORY.setdefault(cid, []).append(t)

# 分类导航颜色
CATEGORY_COLORS = {
    1:  "#4F46E5", 2:  "#059669", 3:  "#D97706", 4:  "#DC2626",
    5:  "#0891B2", 6:  "#7C3AED", 7:  "#DB2777", 8:  "#65A30D",
    9:  "#0D9488", 10: "#9333EA", 11: "#2563EB", 12: "#E11D48",
}

# 分类 SVG 图标（Base64 编码的内联 SVG 或 Unicode 字符）
CATEGORY_ICONS = {
    1:  "🔍", 2:  "📝", 3:  "📋", 4:  "🎙️",
    5:  "⚖️", 6:  "✏️", 7:  "🌐", 8:  "📖",
    9:  "📄", 10: "🗂️", 11: "📊", 12: "🔗",
}
