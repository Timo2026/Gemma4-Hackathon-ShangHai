"""
数据库初始化脚本
"""
from app.core.database import engine, Base, SessionLocal
from app.models.models import User, Document, Tool, IPMaterial, GenerationRecord
from app.core.security import get_password_hash

# 初始化工具数据
INITIAL_TOOLS = [
    {"name": "秘塔 AI 搜索", "category": "法律检索", "url": "https://metaso.cn", "description": "类案检索、法条检索", "sort_order": 1},
    {"name": "法天使案牍", "category": "合同审查", "url": "https://www.fatianshi.cn", "description": "合同风险审查、条款优化", "sort_order": 2},
    {"name": "飞书多维表格", "category": "合同管理", "url": "https://www.feishu.cn", "description": "合同台账管理、到期提醒", "sort_order": 3},
    {"name": "通义听悟", "category": "证据整理", "url": "https://tingwu.aliyun.com", "description": "语音转文字、证据梳理", "sort_order": 4},
    {"name": "北大法宝模拟法庭", "category": "模拟法庭", "url": "https://www.pkulaw.com", "description": "庭审流程模拟、辩论训练", "sort_order": 5},
    {"name": "AlphaGPT", "category": "文书写作", "url": "https://alphalawyer.cn", "description": "法律文书生成", "sort_order": 6},
    {"name": "DeepL", "category": "法律翻译", "url": "https://www.deepl.com", "description": "法律文本精准翻译", "sort_order": 7},
    {"name": "豆包浏览器插件", "category": "材料阅读", "url": "https://www.doubao.com", "description": "长文本摘要、重点标注", "sort_order": 8},
    {"name": "WPS AI", "category": "公文撰写", "url": "https://ai.wps.cn", "description": "法律公文撰写、格式优化", "sort_order": 9},
    {"name": "Get 笔记", "category": "知识管理", "url": "https://getnote.app", "description": "法律知识整理、标签分类", "sort_order": 10},
    {"name": "Mermaid", "category": "文本可视化", "url": "https://mermaid.live", "description": "案情流程图、关系图生成", "sort_order": 11},
    {"name": "微信 AI 输入法", "category": "多端协作", "url": "https://inputmethod.weixin.qq.com", "description": "多端同步、协作编辑", "sort_order": 12},
]


def init_database():
    """初始化数据库：创建表 + 填充基础数据"""
    print("正在创建数据库表...")
    Base.metadata.create_all(bind=engine)
    print("数据库表创建完成！")

    db = SessionLocal()
    try:
        # 填充工具数据
        existing = db.query(Tool).count()
        if existing == 0:
            print("正在初始化工具数据...")
            for t in INITIAL_TOOLS:
                tool = Tool(**t)
                db.add(tool)
            db.commit()
            print(f"已初始化 {len(INITIAL_TOOLS)} 个工具数据！")
        else:
            print(f"工具数据已存在（{existing}条），跳过初始化")

        # 创建测试用户（如果不存在）
        test_user = db.query(User).filter(User.phone == "13800000000").first()
        if not test_user:
            print("正在创建测试用户...")
            user = User(
                phone="13800000000",
                password_hash=get_password_hash("123456"),
                name="测试律师",
                role="premium",
                title="高级合伙人律师",
                practice_years=10,
                education="法学硕士",
                qualifications="律师执业证 A 证, 北京市优秀律师",
                specialties="民商事诉讼, 公司法律顾问, 知识产权",
                bio="拥有10年以上法律从业经验，专注于民商事诉讼和公司法律顾问服务。",
                firm="测试律师事务所",
            )
            db.add(user)
            db.commit()
            print("测试用户创建成功！（手机号: 13800000000, 密码: 123456）")
        else:
            print("测试用户已存在，跳过")

    finally:
        db.close()

    print("\n数据库初始化完成！")
    print("=" * 40)
    print("测试账号: 13800000000 / 123456")
    print("API 文档: http://localhost:8000/docs")
    print("=" * 40)


if __name__ == "__main__":
    init_database()
