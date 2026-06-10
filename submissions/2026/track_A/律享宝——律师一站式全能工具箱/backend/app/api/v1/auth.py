"""
认证 API 路由
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from app.core.security import get_current_user_id
from app.services.auth_service import auth_service

router = APIRouter(prefix="/api/v1/auth", tags=["认证"])


class LoginRequest(BaseModel):
    phone: str = Field(..., description="手机号")
    password: str = Field(..., description="密码")


class RegisterRequest(BaseModel):
    phone: str = Field(..., description="手机号")
    password: str = Field(..., description="密码")
    name: str = Field(default=None, description="姓名")


class ProfileUpdateRequest(BaseModel):
    name: str = Field(default=None, description="姓名")
    avatar: str = Field(default=None, description="头像URL")
    title: str = Field(default=None, description="职称/头衔")
    practice_years: int = Field(default=None, description="执业年限")
    education: str = Field(default=None, description="学历")
    qualifications: str = Field(default=None, description="资质/荣誉")
    specialties: str = Field(default=None, description="擅长领域")
    bio: str = Field(default=None, description="个人简介")
    firm: str = Field(default=None, description="律所名称")
    license: str = Field(default=None, description="执业证号")


@router.post("/register")
def register(req: RegisterRequest):
    """用户注册"""
    return auth_service.register(req.phone, req.password, req.name)


@router.post("/login")
def login(req: LoginRequest):
    """用户登录"""
    return auth_service.login(req.phone, req.password)


@router.get("/profile")
def get_profile(user_id: int = Depends(get_current_user_id)):
    """获取个人信息"""
    return auth_service.get_user_profile(user_id)


@router.put("/profile")
def update_profile(req: ProfileUpdateRequest, user_id: int = Depends(get_current_user_id)):
    """更新个人信息"""
    return auth_service.update_profile(user_id, req.dict(exclude_none=True))
