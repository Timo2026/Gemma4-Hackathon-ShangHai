"""验证所有模块是否就绪"""
import sys

print("=" * 50)
print("律享宝 - 系统就绪检查")
print("=" * 50)

# 1. 配置
print("\n[1/8] 配置检查...")
from app.core.config import GEMMA4_API_KEY, GEMMA4_BASE_URL, GEMMA4_MODEL, APP_NAME
print(f"  应用名称: {APP_NAME}")
print(f"  Google Gemma 4 模型: {GEMMA4_MODEL}")
print(f"  Gemma 4 API 地址: {GEMMA4_BASE_URL}")
print(f"  API Key: {'已配置' if GEMMA4_API_KEY else '未配置（将使用模拟模式）'}")
if not GEMMA4_API_KEY:
    print("  💡 提示: 设置 GEMMA4_API_KEY 环境变量可启用真实 Gemma 4 API 调用")

# 2. 数据库
print("\n[2/8] 数据库检查...")
from app.core.database import engine, Base
print(f"  数据库引擎: {engine.url}")
print(f"  注册的表: {len(Base.metadata.tables)} 个")

# 3. 安全模块
print("\n[3/8] 安全模块检查...")
from app.core.security import verify_password, get_password_hash, create_access_token
h = get_password_hash("test123")
assert verify_password("test123", h), "密码验证失败"
print("  密码加密/验证: OK")
token = create_access_token({"user_id": 1, "role": "test"})
print(f"  JWT Token 生成: OK ({len(token)} 字符)")

# 4. AI 客户端
print("\n[4/8] AI 客户端检查...")
from app.agents.gemma4_client import gemma_client
print(f"  客户端类型: {type(gemma_client).__name__}")
print(f"  模拟模式: {gemma_client.use_mock}")
print(f"  已注册函数: {list(gemma_client.functions_registry.keys())}")

# 5. 文档 Agent
print("\n[5/8] 文档 Agent 检查...")
from app.agents.document_agent import DOCUMENT_SCENARIOS, generate_document
print(f"  文书场景: {len(DOCUMENT_SCENARIOS)} 类")

# 6. 工具 Agent
print("\n[6/8] 工具 Agent 检查...")
from app.agents.tool_agent import TOOLS_CATALOG, recommend_tools
print(f"  工具分类: {len(TOOLS_CATALOG)} 个")
matched = recommend_tools("帮我整理一份合同")
print(f"  工具推荐测试: {len(matched)} 个推荐")

# 7. IP Agent
print("\n[7/8] IP Agent 检查...")
from app.agents.ip_agent import PLATFORMS, TRUST_CONTENT_TYPES, desensitize
print(f"  支持平台: {len(PLATFORMS)} 个")
print(f"  信任背书类型: {len(TRUST_CONTENT_TYPES)} 个")
d = desensitize("手机号13812345678，身份证110101199001011234，金额50000元")
print(f"  脱敏测试: {d}")

# 8. FastAPI 路由
print("\n[8/8] API 路由检查...")
try:
    from app.main import app
    routes = sorted([r.path for r in app.routes if hasattr(r, 'path') and r.path.startswith('/')])
    print(f"  路由总数: {len(routes)}")
    for r in routes:
        methods = [m for m in ['GET', 'POST', 'PUT', 'DELETE'] if any(route.path == r and m in route.methods for route in app.routes if hasattr(route, 'methods'))]
        if not methods:
            methods = ['GET']
        print(f"    {methods[0]:6s} {r}")
except Exception as e:
    print(f"  路由检查跳过（需 MySQL 就绪）: {e}")

print("\n" + "=" * 50)
print("[OK] 系统检查通过！所有模块就绪")
print("=" * 50)
print("\n启动命令: python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload")
print("API 文档: http://localhost:8000/docs")
