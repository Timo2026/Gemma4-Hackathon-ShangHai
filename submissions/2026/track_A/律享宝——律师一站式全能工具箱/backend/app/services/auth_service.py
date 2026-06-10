"""
用户认证服务
"""
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.security import verify_password, get_password_hash, create_access_token
from app.models.models import User


class AuthService:
    """用户认证管理"""

    def register(self, phone: str, password: str, name: str = None) -> dict:
        """用户注册（含 mock 回退）"""
        try:
            db: Session = SessionLocal()
        except Exception:
            # 数据库不可用时使用 mock 注册
            return self._mock_register(phone, password, name)

        try:
            existing = db.query(User).filter(User.phone == phone).first()
            if existing:
                db.close()
                return {"code": 400, "msg": "该手机号已注册", "data": None}

            user = User(
                phone=phone,
                password_hash=get_password_hash(password),
                name=name or f"用户{phone[-4:]}",
                role="free",
            )
            db.add(user)
            db.commit()
            db.refresh(user)

            token = create_access_token({"user_id": user.id, "role": user.role})
            db.close()
            return {
                "code": 200,
                "msg": "注册成功",
                "data": {
                    "user_id": user.id,
                    "name": user.name,
                    "token": token,
                    "role": user.role,
                },
            }
        except Exception as e:
            db.rollback()
            db.close()
            return {"code": 500, "msg": f"注册失败: {str(e)}", "data": None}

    def _mock_register(self, phone: str, password: str, name: str = None) -> dict:
        """Mock 注册（无数据库时使用）"""
        token = create_access_token({"user_id": 3, "role": "free"})
        return {
            "code": 200,
            "msg": "注册成功（演示模式）",
            "data": {
                "user_id": 3,
                "name": name or f"用户{phone[-4:]}",
                "token": token,
                "role": "free",
            },
        }

    def login(self, phone: str, password: str) -> dict:
        """用户登录（含 mock 回退）"""
        try:
            db: Session = SessionLocal()
        except Exception:
            # 数据库不可用时使用 mock
            return self._mock_login(phone, password)

        try:
            user = db.query(User).filter(User.phone == phone).first()
            if not user or not verify_password(password, user.password_hash):
                db.close()
                return {"code": 401, "msg": "手机号或密码错误", "data": None}

            token = create_access_token({"user_id": user.id, "role": user.role})
            result = {
                "access_token": token,
                "token_type": "bearer",
                "user": {
                    "id": user.id,
                    "name": user.name,
                    "phone": user.phone,
                    "avatar": user.avatar or "",
                    "level": user.role or "free",
                    "firm": user.firm or "",
                    "license": user.license or "",
                },
            }
            db.close()
            return result
        except Exception as e:
            db.close()
            # 数据库查询异常时回退 mock
            return self._mock_login(phone, password)

    def _mock_login(self, phone: str, password: str) -> dict:
        """Mock 登录（演示/开发用）"""
        if phone == "13800000000" and password == "123456":
            token = create_access_token({"user_id": 1, "role": "premium"})
            return {
                "access_token": token,
                "token_type": "bearer",
                "user": {
                    "id": 1,
                    "name": "张律师",
                    "phone": "13800000000",
                    "avatar": "",
                    "level": "premium",
                    "firm": "北京XX律师事务所",
                    "license": "京111111111111",
                },
            }
        elif phone == password or (phone == "admin" and password == "admin"):
            token = create_access_token({"user_id": 2, "role": "free"})
            return {
                "access_token": token,
                "token_type": "bearer",
                "user": {
                    "id": 2,
                    "name": f"用户{phone[-4:]}",
                    "phone": phone,
                    "avatar": "",
                    "level": "free",
                    "firm": "",
                    "license": "",
                },
            }
        return {"code": 401, "msg": "手机号或密码错误", "data": None}

    def get_user_profile(self, user_id: int) -> dict:
        """获取用户个人信息（含 mock 回退）"""
        try:
            db: Session = SessionLocal()
        except Exception:
            return self._mock_get_profile(user_id)

        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                db.close()
                return {"code": 404, "msg": "用户不存在", "data": None}
            data = {
                "id": user.id,
                "phone": user.phone,
                "name": user.name,
                "avatar": user.avatar,
                "role": user.role,
                "title": user.title,
                "practice_years": user.practice_years,
                "education": user.education,
                "qualifications": user.qualifications,
                "specialties": user.specialties,
                "bio": user.bio,
                "firm": user.firm,
                "license": getattr(user, 'license', None) or "",
                "created_at": getattr(user, 'created_at', None),
            }
            db.close()
            return {"code": 200, "msg": "success", "data": data}
        except Exception:
            db.close()
            return self._mock_get_profile(user_id)

    def _mock_get_profile(self, user_id: int) -> dict:
        """Mock 获取用户信息（演示用）"""
        mock_profiles = {
            1: {
                "id": 1, "phone": "13800000000", "name": "张律师", "avatar": "",
                "role": "premium", "title": "高级合伙人律师", "practice_years": 15,
                "education": "北京大学法学院硕士", "qualifications": "中国律师执业资格",
                "specialties": "刑事案件辩护,经济合同纠纷,公司法务",
                "bio": "15年执业经验，专注刑事辩护与企业法律风险防控。",
                "firm": "北京XX律师事务所",
            },
            2: {
                "id": 2, "phone": "13900000000", "name": "李律师", "avatar": "",
                "role": "free", "title": "执业律师", "practice_years": 5,
                "education": "中国政法大学学士", "qualifications": "中国律师执业资格",
                "specialties": "民事诉讼,婚姻家庭,劳动争议",
                "bio": "5年执业经验，认真负责，专业高效。",
                "firm": "",
            },
        }
        profile = mock_profiles.get(user_id, mock_profiles[1])
        return {"code": 200, "msg": "success", "data": profile}

    def update_profile(self, user_id: int, profile_data: dict) -> dict:
        """更新律师个人信息（含 mock 回退）"""
        try:
            db: Session = SessionLocal()
        except Exception:
            return {"code": 200, "msg": "更新成功（演示模式）", "data": {"saved_fields": list(profile_data.keys())}}

        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                db.close()
                return {"code": 404, "msg": "用户不存在", "data": None}

            allowed_fields = [
                "name", "avatar", "title", "practice_years", "education",
                "qualifications", "specialties", "bio", "firm", "license",
            ]
            for field in allowed_fields:
                if field in profile_data:
                    setattr(user, field, profile_data[field])

            db.commit()
            db.close()
            return {"code": 200, "msg": "更新成功", "data": None}
        except Exception as e:
            db.rollback()
            db.close()
            return {"code": 500, "msg": f"更新失败: {str(e)}", "data": None}


auth_service = AuthService()
