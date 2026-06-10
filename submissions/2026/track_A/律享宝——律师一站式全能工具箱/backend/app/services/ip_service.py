"""
律师 IP 智能运营服务
"""
from app.core.database import SessionLocal
from app.models.models import IPMaterial, GenerationRecord
from app.agents.ip_agent import (
    generate_profile,
    generate_case_description,
    generate_platform_material,
    generate_trust_content,
    generate_publish_strategy,
    PLATFORMS,
    TRUST_CONTENT_TYPES,
)


class IPService:
    """律师 IP 运营管理"""

    def get_platforms(self) -> dict:
        """获取支持的平台列表"""
        return {"code": 200, "msg": "success", "data": {"platforms": PLATFORMS}}

    def get_trust_types(self) -> dict:
        """获取信任背书文案类型"""
        return {"code": 200, "msg": "success", "data": {"types": TRUST_CONTENT_TYPES}}

    def generate_profile_packaging(self, user_id: int, lawyer_info: dict) -> dict:
        """生成个人简介包装"""
        try:
            result = generate_profile(lawyer_info)
            try:
                self._save_record(user_id, "ip", {"action": "profile", "input": lawyer_info}, result)
            except Exception:
                pass
            return {"code": 200, "msg": "生成成功", "data": result}
        except Exception as e:
            return {"code": 500, "msg": f"生成失败: {str(e)}", "data": None}

    def generate_case(self, user_id: int, case_info: dict) -> dict:
        """生成合规案例描述"""
        try:
            result = generate_case_description(case_info)
            try:
                self._save_record(user_id, "ip", {"action": "case", "input": case_info}, result)
            except Exception:
                pass
            return {"code": 200, "msg": "生成成功", "data": result}
        except Exception as e:
            return {"code": 500, "msg": f"生成失败: {str(e)}", "data": None}

    def generate_material(self, user_id: int, lawyer_info: dict, platform: str, material_type: str = "auto") -> dict:
        """生成指定平台宣传素材"""
        try:
            result = generate_platform_material(lawyer_info, platform, material_type)
            try:
                self._save_material(user_id, platform, result)
                self._save_record(user_id, "ip", {"action": "material", "platform": platform, "input": lawyer_info}, result)
            except Exception:
                pass
            return {"code": 200, "msg": "生成成功", "data": result}
        except Exception as e:
            return {"code": 500, "msg": f"生成失败: {str(e)}", "data": None}

    def generate_trust_content(self, user_id: int, lawyer_info: dict, content_type: str) -> dict:
        """生成信任背书文案"""
        try:
            result = generate_trust_content(lawyer_info, content_type)
            try:
                self._save_record(user_id, "ip", {"action": "trust", "type": content_type, "input": lawyer_info}, result)
            except Exception:
                pass
            return {"code": 200, "msg": "生成成功", "data": result}
        except Exception as e:
            return {"code": 500, "msg": f"生成失败: {str(e)}", "data": None}

    def generate_strategy(self, user_id: int, lawyer_info: dict) -> dict:
        """生成发布策略"""
        try:
            result = generate_publish_strategy(lawyer_info)
            try:
                self._save_record(user_id, "ip", {"action": "strategy", "input": lawyer_info}, result)
            except Exception:
                pass
            return {"code": 200, "msg": "生成成功", "data": result}
        except Exception as e:
            return {"code": 500, "msg": f"生成失败: {str(e)}", "data": None}

    def list_materials(self, user_id: int, page: int = 1, size: int = 20) -> dict:
        """获取用户的IP素材列表（DB 不可用时返回空列表）"""
        try:
            db = SessionLocal()
        except Exception:
            return {"code": 200, "msg": "success", "data": {"items": [], "total": 0, "page": page, "size": size}}
        try:
            query = db.query(IPMaterial).filter(IPMaterial.user_id == user_id).order_by(IPMaterial.created_at.desc())
            total = query.count()
            items = query.offset((page - 1) * size).limit(size).all()
            return {
                "code": 200,
                "msg": "success",
                "data": {
                    "items": [
                        {
                            "id": m.id,
                            "platform": m.platform,
                            "material_type": m.material_type,
                            "title": m.title,
                            "status": m.status,
                            "publish_time": m.publish_time.isoformat() if m.publish_time else None,
                            "created_at": m.created_at.isoformat() if m.created_at else None,
                        }
                        for m in items
                    ],
                    "total": total,
                    "page": page,
                    "size": size,
                },
            }
        finally:
            db.close()

    def _save_material(self, user_id: int, platform: str, material_data: dict):
        try:
            db = SessionLocal()
        except Exception:
            return
        try:
            material = IPMaterial(
                user_id=user_id,
                platform=platform,
                material_type=material_data.get("material_type", "auto"),
                title=material_data.get("title", ""),
                content=material_data.get("content", ""),
                image_url=material_data.get("image_description", ""),
                status="draft",
            )
            db.add(material)
            db.commit()
        finally:
            db.close()

    def _save_record(self, user_id: int, module: str, input_data: dict, result: dict):
        try:
            db = SessionLocal()
        except Exception:
            return
        try:
            record = GenerationRecord(
                user_id=user_id,
                module=module,
                input_data=input_data,
                output_data=result,
                model="gemma-4-14b",
                tokens_used=result.get("tokens_used", 0),
                latency_ms=result.get("latency_ms", 0),
            )
            db.add(record)
            db.commit()
        finally:
            db.close()


ip_service = IPService()
