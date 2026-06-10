"""
法律工具智能编排 Agent（P0）
基于 Google Gemma 4 工具编排能力，统一调度法律 AI 工具并生成保姆级教程
"""
from app.agents.gemma4_client import gemma_client

# 11 大类法律 AI 工具
TOOLS_CATALOG = [
    {"category": "法律检索", "name": "秘塔 AI 搜索", "url": "https://metaso.cn", "tags": "类案检索,法条检索"},
    {"category": "合同审查", "name": "法天使案牍", "url": "https://www.fatianshi.cn", "tags": "合同风险审查,条款优化"},
    {"category": "合同管理", "name": "飞书多维表格", "url": "https://www.feishu.cn", "tags": "合同台账,到期提醒"},
    {"category": "证据整理", "name": "通义听悟", "url": "https://tingwu.aliyun.com", "tags": "语音转文字,证据梳理"},
    {"category": "模拟法庭", "name": "北大法宝模拟法庭", "url": "https://www.pkulaw.com", "tags": "庭审模拟,辩论训练"},
    {"category": "文书写作", "name": "AlphaGPT", "url": "https://alphalawyer.cn", "tags": "法律文书生成"},
    {"category": "法律翻译", "name": "DeepL", "url": "https://www.deepl.com", "tags": "精准翻译"},
    {"category": "材料阅读", "name": "豆包浏览器插件", "url": "https://www.doubao.com", "tags": "长文本摘要,标注"},
    {"category": "公文撰写", "name": "WPS AI", "url": "https://ai.wps.cn", "tags": "公文撰写,格式优化"},
    {"category": "知识管理", "name": "Get 笔记", "url": "https://getnote.app", "tags": "知识整理,标签分类"},
    {"category": "文本可视化", "name": "Mermaid", "url": "https://mermaid.live", "tags": "流程图,关系图"},
    {"category": "多端协作", "name": "微信 AI 输入法", "url": "https://inputmethod.weixin.qq.com", "tags": "多端同步,协作"},
]

SYSTEM_PROMPT = """你是一名法律科技工具专家，精通市面上所有法律 AI 工具的使用方法。
你的任务是根据用户需求，推荐合适的工具组合，并生成零基础、"一步一图"的保姆级操作教程。

核心要求：
1. 全程使用通俗语言，避免专业术语
2. 每步明确说明：点击哪里、选择什么、得到什么结果
3. 附带新手常见错误和避坑指南
4. 单套教程不超过 10 步
5. 提供官方正版工具网址"""


def recommend_tools(user_need: str) -> list:
    """
    根据用户需求推荐合适的工具
    """
    user_need_lower = user_need.lower()

    # 简单的关键词匹配（实际使用 Gemma 4 智能推荐）
    keyword_map = {
        "录音": "通义听悟",
        "转文字": "通义听悟",
        "语音": "通义听悟",
        "证据": "通义听悟",
        "合同": "法天使案牍",
        "审查": "法天使案牍",
        "翻译": "DeepL",
        "英文": "DeepL",
        "流程图": "Mermaid",
        "关系图": "Mermaid",
        "可视化": "Mermaid",
        "摘要": "豆包",
        "总结": "豆包",
        "检索": "秘塔",
        "搜索": "秘塔",
        "笔记": "Get 笔记",
        "整理": "Get 笔记",
        "公文": "WPS AI",
        "格式": "WPS AI",
    }

    matched = []
    matched_names = set()
    for keyword, tool_name in keyword_map.items():
        if keyword in user_need_lower and tool_name not in matched_names:
            for t in TOOLS_CATALOG:
                if t["name"] == tool_name:
                    matched.append(t)
                    matched_names.add(tool_name)
                    break

    if not matched:
        # 无匹配时返回全部（取前 3 个分类）
        seen_cats = set()
        for t in TOOLS_CATALOG:
            if t["category"] not in seen_cats and len(matched) < 3:
                matched.append(t)
                seen_cats.add(t["category"])

    return matched


def generate_tutorial(tool: dict, user_need: str) -> str:
    """
    为指定工具生成保姆级教程
    """
    user_input = f"""用户需求：{user_need}
推荐工具：{tool['name']}
工具网址：{tool['url']}
工具功能：{tool['tags']}

请生成一份零基础、'一步一图'的保姆级操作教程，不超过 10 步。"""

    prompt = SYSTEM_PROMPT + f"""

请根据以下格式输出教程：

## 📋 工具名称
## 🎯 它能做什么
## 📝 操作步骤（每步格式：第N步 | 操作说明 | 预期结果）
## ⚠️ 新手常见错误（避坑指南）
## 🔗 官方地址"""

    result = gemma_client.generate(prompt, user_input)
    return result["content"]


def orchestrate_tools(user_need: str) -> dict:
    """
    工具编排主流程
    1. 分析需求 → 2. 推荐工具 → 3. 规划流程 → 4. 生成教程 → 5. 整合结果
    """
    tools = recommend_tools(user_need)

    tutorials = []
    for tool in tools:
        tutorial = generate_tutorial(tool, user_need)
        tutorials.append({
            "tool_name": tool["name"],
            "tool_url": tool["url"],
            "tutorial": tutorial,
        })

    # 生成整合方案
    plan_prompt = f"""用户需求：{user_need}
推荐工具：{[t['name'] for t in tools]}

请制定一个完整的工作流程方案，说明如何使用以上工具组合完成任务，包括先后顺序、数据流转。"""

    plan = gemma_client.generate(SYSTEM_PROMPT, plan_prompt)

    return {
        "user_need": user_need,
        "recommended_tools": [{"name": t["name"], "url": t["url"], "category": t["category"]} for t in tools],
        "workflow_plan": plan["content"],
        "tutorials": tutorials,
        "tokens_used": plan["tokens_used"],
        "latency_ms": plan["latency_ms"],
    }
