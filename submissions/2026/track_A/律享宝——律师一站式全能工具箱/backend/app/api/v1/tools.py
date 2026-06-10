"""
法律工具 API 路由
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from app.core.security import get_current_user_id
from app.services.tool_service import tool_service
from app.data.navigation_data import CATEGORIES, TOOLS, TOOLS_BY_CATEGORY, CATEGORY_COLORS, CATEGORY_ICONS
from app.agents.gemma4_client import gemma_client

router = APIRouter(prefix="/api/v1/tools", tags=["法律工具"])


class OrchestrateRequest(BaseModel):
    query: str = Field(..., description="用户需求描述（自然语言）")


class AiTutorialRequest(BaseModel):
    tool_name: str = Field(default="", description="工具名称")
    tool_url: str = Field(default="", description="工具官方网址")
    question: str = Field(..., description="用户的具体需求描述")


@router.get("/catalog")
def get_catalog():
    """获取工具分类目录（11大类）"""
    return tool_service.get_catalog()


@router.get("/navigation")
def get_navigation():
    """获取首页导航数据（12大分类 + 27个工具，含Logo/官网/教程）"""
    categories = []
    for cat in CATEGORIES:
        cid = cat["id"]
        tools = TOOLS_BY_CATEGORY.get(cid, [])
        categories.append({
            "id": cid,
            "name": cat["name"],
            "icon": CATEGORY_ICONS.get(cid, "🔧"),
            "color": CATEGORY_COLORS.get(cid, "#4F46E5"),
            "tools": tools,
        })
    return {
        "code": 200,
        "msg": "success",
        "data": {
            "categories": categories,
            "total_categories": len(CATEGORIES),
            "total_tools": len(TOOLS),
        },
    }


@router.post("/orchestrate")
def orchestrate(req: OrchestrateRequest, user_id: int = Depends(get_current_user_id)):
    """工具编排：推荐工具 + 生成教程 + 规划流程"""
    return tool_service.orchestrate(user_id, req.query)


@router.post("/ai-tutorial")
def ai_tutorial(req: AiTutorialRequest, user_id: int = Depends(get_current_user_id)):
    """AI 定制教程：基于 Google Gemma 4 根据用户具体需求生成个性化工具教程"""
    system_prompt = """你是一名法律科技工具专家，精通市面上所有法律 AI 工具的使用方法。
你的任务是根据用户的特定需求，结合工具的通用教程，生成针对性的个性化操作指南。

核心要求：
1. 全程使用通俗语言，避免专业术语
2. 每步明确说明：点击哪里、选择什么、得到什么结果
3. 针对用户的具体需求场景定制步骤
4. 附带注意事项和常见问题
5. 所有内容由 Google Gemma 4 生成"""

    user_input = f"""请为以下工具生成一份针对用户具体需求的定制化教程：

工具名称：{req.tool_name}
工具网址：{req.tool_url}
用户的具体需求：{req.question}

请按照以下格式输出：
## 🎯 针对你的需求，操作步骤
## ⚠️ 注意事项
## ❓ 常见问题"""

    result = gemma_client.generate(system_prompt, user_input)

    return {
        "code": 200,
        "msg": "success",
        "data": {
            "tutorial": result["content"],
            "tool_name": req.tool_name,
            "model": "Google Gemma 4 14B",
            "tokens_used": result["tokens_used"],
            "latency_ms": result["latency_ms"],
        },
    }
