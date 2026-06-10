"""
法律文档 API 路由
"""
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from app.core.security import get_current_user_id
from app.services.document_service import document_service

router = APIRouter(prefix="/api/v1/documents", tags=["法律文书"])


class GenerateRequest(BaseModel):
    scenario: str = Field(default="", description="文书场景（21类）")
    title: str = Field(default="", description="案件标题")
    parties: str = Field(default="", description="当事人基本情况")
    facts: str = Field(..., description="案件基本事实与诉求")
    laws: str = Field(default="", description="适用法律")
    # 兼容旧字段
    case_type: str = Field(default="", description="案件类型/案由（兼容）")
    issues: str = Field(default="", description="争议焦点/核心问题（兼容）")
    evidence: str = Field(default="", description="现有证据情况（兼容）")
    stage: str = Field(default="一审", description="案件阶段: 侦查/审查起诉/一审/二审/执行")
    remarks: str = Field(default="", description="特殊情节备注")


@router.get("/scenarios")
def get_scenarios():
    """获取文书场景列表（21类）"""
    return document_service.get_scenarios()


@router.post("/generate")
def generate_doc(req: GenerateRequest, user_id: int = Depends(get_current_user_id)):
    """生成法律文书"""
    return document_service.generate(user_id, req.dict())


@router.get("")
def list_documents(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    user_id: int = Depends(get_current_user_id),
):
    """获取文书列表"""
    return document_service.list_documents(user_id, page, size)


@router.get("/{doc_id}")
def get_document(doc_id: int, user_id: int = Depends(get_current_user_id)):
    """获取单篇文书详情"""
    return document_service.get_document(doc_id)
