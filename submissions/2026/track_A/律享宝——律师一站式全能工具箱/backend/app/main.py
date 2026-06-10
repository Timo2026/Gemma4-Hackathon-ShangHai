"""
律享宝 - FastAPI 应用入口
"""
import uvicorn
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import APP_NAME, APP_VERSION, DEBUG
from app.core.database import engine, Base
from app.api.v1 import auth, documents, tools, ip, templates

# 创建数据库表（连接失败时仅记录日志，不影响启动）
try:
    Base.metadata.create_all(bind=engine)
    logging.info("数据库表创建/检查完成")
except Exception as e:
    logging.warning(f"数据库表创建失败（启动后仍可正常工作）: {e}")

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="基于 Google Gemma 4 的全链路律师执业 AI Agent — Google Gemma 4 开发大赛参赛项目",
    docs_url="/docs" if DEBUG else "/docs",
    redoc_url="/redoc" if DEBUG else None,
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(tools.router)
app.include_router(ip.router)
app.include_router(templates.router)


@app.get("/")
def root():
    """根路径 - 健康检查"""
    return {
        "app": APP_NAME,
        "version": APP_VERSION,
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
def health_check():
    """健康检查接口"""
    return {"status": "healthy", "app": APP_NAME, "version": APP_VERSION}


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=DEBUG,
        log_level="info",
    )
