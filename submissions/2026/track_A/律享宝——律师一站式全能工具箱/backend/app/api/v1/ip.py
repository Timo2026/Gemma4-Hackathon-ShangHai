"""
律师 IP 运营 API 路由
"""
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from app.core.security import get_current_user_id
from app.services.ip_service import ip_service

router = APIRouter(prefix="/api/v1/ip", tags=["IP运营"])


class LawyerInfo(BaseModel):
    name: str = Field(default="", description="姓名")
    practice_years: int = Field(default=None, description="执业年限")
    education: str = Field(default="", description="学历")
    qualifications: str = Field(default="", description="资质/荣誉")
    specialties: str = Field(default="", description="擅长领域")
    bio: str = Field(default="", description="个人简介")
    firm: str = Field(default="", description="执业机构")
    target_clients: str = Field(default="", description="目标客户")
    # V1.1 新增字段
    experience: str = Field(default="", description="执业经验描述")
    specialty: str = Field(default="", description="擅长领域（别名）")


class CaseInfo(BaseModel):
    case_type: str = Field(..., description="案例类型")
    result: str = Field(..., description="案件结果")
    client_feedback: str = Field(default="", description="客户评价")
    parties: str = Field(default="", description="涉及人物（将被脱敏）")
    # V1.1 新增字段
    name: str = Field(default="", description="案例名称")
    description: str = Field(default="", description="案件描述")
    desensitize: bool = Field(default=True, description="是否自动脱敏")


class StrategyRequest(BaseModel):
    """V1.1 综合策略请求，接受 profile + cases"""
    profile: LawyerInfo = Field(default=None, description="律师个人信息")
    cases: list = Field(default=[], description="成功案例列表")


class MaterialRequest(BaseModel):
    platform: str = Field(..., description="目标平台")
    material_type: str = Field(default="auto", description="素材类型")
    lawyer_info: LawyerInfo


class TrustContentRequest(BaseModel):
    content_type: str = Field(..., description="信任背书类型")
    lawyer_info: LawyerInfo


@router.get("/platforms")
def get_platforms():
    """获取支持的发布平台列表"""
    return ip_service.get_platforms()


@router.get("/trust-types")
def get_trust_types():
    """获取信任背书文案类型"""
    return ip_service.get_trust_types()


@router.post("/profile")
def generate_profile(req: LawyerInfo, user_id: int = Depends(get_current_user_id)):
    """生成个人简介包装"""
    return ip_service.generate_profile_packaging(user_id, req.dict())


@router.post("/case")
def generate_case(req: CaseInfo, user_id: int = Depends(get_current_user_id)):
    """生成合规案例描述"""
    return ip_service.generate_case(user_id, req.dict())


@router.post("/material")
def generate_material(req: MaterialRequest, user_id: int = Depends(get_current_user_id)):
    """生成指定平台宣传素材"""
    return ip_service.generate_material(user_id, req.lawyer_info.dict(), req.platform, req.material_type)


@router.post("/trust-content")
def generate_trust(req: TrustContentRequest, user_id: int = Depends(get_current_user_id)):
    """生成信任背书文案"""
    return ip_service.generate_trust_content(user_id, req.lawyer_info.dict(), req.content_type)


@router.post("/strategy")
def generate_strategy(req: StrategyRequest, user_id: int = Depends(get_current_user_id)):
    """生成内容发布策略（V1.1 支持 profile + cases 组合）"""
    # 兼容：如果通过 StrategyRequest 传入 profile + cases
    lawyer_info = {}
    if req.profile:
        lawyer_info = req.profile.dict()
    elif req.cases and not req.profile:
        # 兼容旧版直接传 LawyerInfo 的情况
        pass
    
    # 合并 cases 信息
    if req.cases:
        lawyer_info["cases"] = req.cases
    
    return ip_service.generate_strategy(user_id, lawyer_info)


@router.get("/materials")
def list_materials(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    user_id: int = Depends(get_current_user_id),
):
    """获取IP素材列表"""
    return ip_service.list_materials(user_id, page, size)
