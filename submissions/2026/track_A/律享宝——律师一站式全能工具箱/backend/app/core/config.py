import os
from dotenv import load_dotenv

load_dotenv()

# Database — 默认使用 SQLite，零依赖启动；生产环境可切换 MySQL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./lvxiangbao.db")

# Redis（可选，本地开发不依赖）
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Google Gemma 4 — 通过 OpenAI 兼容 API 调用（GMI Cloud / Google AI Studio 等）
GEMMA4_API_KEY = os.getenv("GEMMA4_API_KEY", os.getenv("GMI_API_KEY", ""))
GEMMA4_BASE_URL = os.getenv("GEMMA4_BASE_URL", os.getenv("GMI_BASE_URL", "https://api.gmi.cloud/v1"))
GEMMA4_MODEL = os.getenv("GEMMA4_MODEL", "gemma-4-14b")

# 兼容旧变量名
GMI_API_KEY = GEMMA4_API_KEY
GMI_BASE_URL = GEMMA4_BASE_URL
GMI_MODEL = GEMMA4_MODEL

# JWT
SECRET_KEY = os.getenv("SECRET_KEY", "lvxiangbao-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

# OSS
OSS_ENDPOINT = os.getenv("OSS_ENDPOINT", "")
OSS_BUCKET = os.getenv("OSS_BUCKET", "lvxiangbao")

# App
APP_NAME = "律享宝"
APP_VERSION = "1.0.0"
DEBUG = os.getenv("DEBUG", "true").lower() == "true"
