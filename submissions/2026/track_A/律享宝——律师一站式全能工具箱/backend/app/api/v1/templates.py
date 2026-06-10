"""
律享宝 V1.2 - 法律文书模板库 API 路由
"""
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from app.core.security import get_current_user_id
from app.services.template_service import render_template, TemplateRenderError
from app.data.template_data import get_template_list, get_template_detail, TEMPLATE_CATEGORIES

router = APIRouter(prefix="/api/v1/templates", tags=["文书模板库"])


@router.get("/categories")
def get_categories():
    """获取模板分类树"""
    return {"code": 200, "msg": "success", "data": {"categories": TEMPLATE_CATEGORIES}}


@router.get("")
def list_templates(
    category: str = Query(None, description="大类筛选: civil/legal_aid/lawyer"),
    sub_category: str = Query(None, description="子类筛选"),
    keyword: str = Query(None, description="关键词搜索"),
):
    """获取模板列表"""
    templates = get_template_list(category=category, sub_category=sub_category, keyword=keyword)
    # 列表模式只返回摘要
    items = [
        {
            "id": t["id"],
            "name": t["name"],
            "category": t["category"],
            "sub_category": t.get("sub_category", ""),
            "source": t.get("source", ""),
            "scene": t.get("scene", ""),
        }
        for t in templates
    ]
    return {"code": 200, "msg": "success", "data": {"items": items, "total": len(items)}}


@router.get("/{template_id}")
def get_template(template_id: str):
    """获取模板详情（含完整字段定义）"""
    detail = get_template_detail(template_id)
    if not detail:
        return {"code": 404, "msg": "模板不存在", "data": None}
    return {"code": 200, "msg": "success", "data": detail}


class RenderRequest(BaseModel):
    template_id: str = Field(..., description="模板ID")
    form_data: dict = Field(..., description="表单数据")


@router.post("/render")
def render_doc(req: RenderRequest, user_id: int = Depends(get_current_user_id)):
    """渲染模板：填写表单 → 生成文书"""
    try:
        result = render_template(req.template_id, req.form_data)
        return {"code": 200, "msg": "渲染成功", "data": result}
    except TemplateRenderError as e:
        return {"code": 400, "msg": str(e), "data": None}
    except Exception as e:
        return {"code": 500, "msg": f"渲染失败: {str(e)}", "data": None}
