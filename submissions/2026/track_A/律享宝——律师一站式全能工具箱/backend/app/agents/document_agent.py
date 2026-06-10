"""
法律文档智能生成 Agent（P0）
基于 Google Gemma 4 多步规划推理，21 类法律文书端到端生成
"""
from app.agents.gemma4_client import gemma_client

# 21 类法律文书场景
DOCUMENT_SCENARIOS = [
    "类案检索报告", "案件汇报提纲", "调研报告及检察(司法)建议",
    "分析侦查(调查)数据", "侦查(调查)方案", "对犯罪嫌疑人画像",
    "侦查(调查)讯问笔录提纲", "审查报告", "量刑测算",
    "起诉书", "庭审讯问、询问提纲", "公诉意见书",
    "不起诉决定书、不起诉理由说明书", "刑事抗诉书",
    "刑事会见提纲", "质证意见", "辩护发问提纲",
    "辩护词", "审理报告", "裁判文书", "民事调解书",
]

# 文档输入 Schema
INPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "case_type": {"type": "string", "description": "案件类型/案由"},
        "parties": {"type": "string", "description": "当事人基本情况"},
        "facts": {"type": "string", "description": "案件基本事实"},
        "issues": {"type": "string", "description": "争议焦点/核心问题"},
        "evidence": {"type": "string", "description": "现有证据情况"},
        "stage": {"type": "string", "description": "案件阶段: 侦查/审查起诉/一审/二审/执行"},
        "remarks": {"type": "string", "description": "特殊情节备注"},
    },
    "required": ["case_type", "facts", "issues", "stage"],
}

# 文档输出 Schema
OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string", "description": "标准公文标题"},
        "party_info": {"type": "string", "description": "当事人信息"},
        "summary": {"type": "string", "description": "案情摘要"},
        "core_issues": {"type": "string", "description": "核心争议焦点"},
        "body": {"type": "string", "description": "正文完整内容"},
        "legal_basis": {"type": "string", "description": "法律依据引用"},
        "risk_tips": {"type": "string", "description": "风险提示/办案建议"},
        "signature": {"type": "string", "description": "标准化落款"},
        "compliance_check": {"type": "string", "description": "合规校验结果"},
    },
    "required": ["title", "body", "legal_basis"],
}

SYSTEM_PROMPT = """你是一名资深中国法律文书专家，精通中国司法体系和法律文书规范。
你的任务是严格遵循中国法律法规和律师执业规范，生成高质量的法律文书。

工作流程：
1. 提取案件关键要素（案由、当事人、事实、争议焦点、证据、阶段）
2. 分析法律关系，识别适用的法律法规
3. 规划文书标准结构
4. 生成符合司法规范的完整文书
5. 进行合规性校验

核心要求：
- 所有内容必须符合中国法律法规
- 语言严谨、格式规范
- 引用准确的法律条文
- 不得泄露当事人隐私信息
- 输出格式为结构化 JSON"""


def generate_document(input_data: dict) -> dict:
    """
    生成法律文书
    Args:
        input_data: 包含 case_type, parties, facts, issues, evidence, stage, remarks
    Returns:
        生成的文书内容（JSON 结构化）
    """
    scenario = input_data.get('scenario', '') or input_data.get('case_type', '')
    title = input_data.get('title', '')
    parties = input_data.get('parties', '未提供')
    facts = input_data.get('facts', '')
    issues = input_data.get('issues', '')
    evidence = input_data.get('evidence', '未提供')
    stage = input_data.get('stage', '一审')
    remarks = input_data.get('remarks', '未提供')
    laws = input_data.get('laws', '')

    user_input = f"""请根据以下案件信息生成法律文书：

文书场景：{scenario}
案件标题：{title}
当事人信息：{parties}
案件事实与诉求：{facts}
争议焦点：{issues or '从事实中提取'}
证据情况：{evidence}
案件阶段：{stage}
适用法律：{laws or '请根据案件事实检索适用法律'}
特殊备注：{remarks}
"""

    # 注册函数：类案检索
    gemma_client.register_function(
        "search_case_law",
        lambda q, k=5: f"（模拟）检索到与'{q}'相关的{k}个类案",
        "检索中国裁判文书网的同类案件",
    )

    # 注册函数：法规检索
    gemma_client.register_function(
        "search_law",
        lambda q: f"（模拟）检索到与'{q}'相关的法律法规",
        "检索相关法律法规",
    )

    functions = [
        {
            "name": "search_case_law",
            "description": "检索中国裁判文书网的同类案件",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "检索关键词"},
                    "top_k": {"type": "integer", "description": "返回数量"},
                },
                "required": ["query"],
            },
        },
        {
            "name": "search_law",
            "description": "检索相关法律法规",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "检索关键词"},
                },
                "required": ["query"],
            },
        },
    ]

    result = gemma_client.generate_structured(SYSTEM_PROMPT, user_input, OUTPUT_SCHEMA)

    return {
        "document_id": None,  # 由调用方补充
        "title": result["parsed"].get("title", ""),
        "content": result["content"],
        "structured": result["parsed"],
        "tokens_used": result["tokens_used"],
        "latency_ms": result["latency_ms"],
    }
