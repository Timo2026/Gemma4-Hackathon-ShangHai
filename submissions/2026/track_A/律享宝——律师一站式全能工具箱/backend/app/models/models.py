import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Enum as SAEnum, Text as JSON
from sqlalchemy.sql import func
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    phone = Column(String(20), unique=True, nullable=False, comment="手机号")
    password_hash = Column(String(256), nullable=False, comment="密码哈希")
    name = Column(String(100), comment="姓名")
    avatar = Column(String(500), comment="头像URL")
    role = Column(String(20), default="free", comment="会员等级 free/monthly/yearly/premium")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # 律师个人信息（IP运营用）
    title = Column(String(100), comment="职称/头衔")
    practice_years = Column(Integer, comment="执业年限")
    education = Column(String(200), comment="学历")
    qualifications = Column(Text, comment="资质/荣誉")
    specialties = Column(Text, comment="擅长领域")
    bio = Column(Text, comment="个人简介")
    firm = Column(String(200), comment="律所名称")


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    case_type = Column(String(100), comment="案件类型")
    title = Column(String(500), comment="文书标题")
    content = Column(Text, comment="文书内容（Markdown格式）")
    stage = Column(String(50), comment="案件阶段")
    template_id = Column(Integer, comment="模板ID")
    status = Column(String(20), default="completed", comment="draft/completed")
    created_at = Column(DateTime, server_default=func.now())


class Tool(Base):
    __tablename__ = "tools"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, comment="工具名称")
    category = Column(String(50), comment="分类")
    url = Column(String(500), comment="官方网址")
    description = Column(Text, comment="功能描述")
    icon = Column(String(500), comment="图标URL")
    tutorial_url = Column(String(500), comment="图文教程URL")
    video_url = Column(String(500), comment="视频教程URL")
    sort_order = Column(Integer, default=0)
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, server_default=func.now())


class IPMaterial(Base):
    __tablename__ = "ip_materials"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    platform = Column(String(50), comment="目标平台")
    material_type = Column(String(50), comment="素材类型：profile/case/poster/script")
    title = Column(String(500), comment="标题")
    content = Column(Text, comment="内容")
    image_url = Column(String(500), comment="配图URL")
    status = Column(String(20), default="draft", comment="draft/published")
    publish_time = Column(DateTime, comment="发布时间")
    created_at = Column(DateTime, server_default=func.now())


class GenerationRecord(Base):
    __tablename__ = "generation_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    module = Column(String(50), comment="模块: document/tool/ip")
    input_data = Column(Text, comment="输入数据(JSON)")
    output_data = Column(Text, comment="输出数据(JSON)")
    model = Column(String(50), default="gemma-4-14b", comment="使用的模型")
    tokens_used = Column(Integer, comment="Token消耗")
    latency_ms = Column(Integer, comment="响应延迟(ms)")
    created_at = Column(DateTime, server_default=func.now())
