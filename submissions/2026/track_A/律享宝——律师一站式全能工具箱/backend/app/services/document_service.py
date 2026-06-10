"""
法律文档服务
"""
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.models import Document, GenerationRecord
from app.agents.document_agent import generate_document, DOCUMENT_SCENARIOS


class DocumentService:
    """法律文档生成与管理"""

    def get_scenarios(self) -> dict:
        """获取文书场景列表"""
        return {"code": 200, "msg": "success", "data": {"scenarios": DOCUMENT_SCENARIOS, "total": len(DOCUMENT_SCENARIOS)}}

    def generate(self, user_id: int, input_data: dict) -> dict:
        """生成法律文书（DB 不可用时返回 Mock 结果）"""
        try:
            result = generate_document(input_data)
        except Exception as e:
            return {"code": 500, "msg": f"生成失败: {str(e)}", "data": None}

        # DB 保存为可选操作：成功则返回 doc_id，失败不阻断流程
        doc_id = None
        try:
            doc_id = self._save_document(user_id, input_data, result)
            self._save_record(user_id, "document", input_data, result)
        except Exception:
            pass  # 无数据库时仅跳过保存，仍返回生成结果

        if doc_id:
            result["document_id"] = doc_id
        return {"code": 200, "msg": "生成成功", "data": result}

    def _save_document(self, user_id: int, input_data: dict, result: dict) -> int:
        """保存文书到数据库（失败时返回 0）"""
        try:
            db: Session = SessionLocal()
        except Exception:
            return 0
        try:
            doc = Document(
                user_id=user_id,
                case_type=input_data.get("case_type", ""),
                title=result.get("title", result.get("structured", {}).get("title", "")),
                content=result.get("content", ""),
                stage=input_data.get("stage", ""),
            )
            db.add(doc)
            db.commit()
            db.refresh(doc)
            return doc.id
        finally:
            db.close()

    def _save_record(self, user_id: int, module: str, input_data: dict, result: dict):
        """保存生成记录到数据库（失败时静默跳过）"""
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

    def list_documents(self, user_id: int, page: int = 1, size: int = 20) -> dict:
        """获取用户的文书列表（DB 不可用时返回空列表）"""
        try:
            db: Session = SessionLocal()
        except Exception:
            return {"code": 200, "msg": "success", "data": {"items": [], "total": 0, "page": page, "size": size}}
        try:
            query = db.query(Document).filter(Document.user_id == user_id).order_by(Document.created_at.desc())
            total = query.count()
            docs = query.offset((page - 1) * size).limit(size).all()
            return {
                "code": 200,
                "msg": "success",
                "data": {
                    "items": [
                        {
                            "id": d.id,
                            "case_type": d.case_type,
                            "title": d.title,
                            "stage": d.stage,
                            "status": d.status,
                            "created_at": d.created_at.isoformat() if d.created_at else None,
                        }
                        for d in docs
                    ],
                    "total": total,
                    "page": page,
                    "size": size,
                },
            }
        finally:
            db.close()

    def get_document(self, doc_id: int) -> dict:
        """获取单篇文书详情（DB 不可用时返回模拟数据）"""
        try:
            db: Session = SessionLocal()
        except Exception:
            return {"code": 200, "msg": "success（演示模式）", "data": {
                "id": doc_id, "case_type": "模拟案件", "title": "模拟文书",
                "content": "（数据库未连接，此为演示内容。连接 MySQL 后可查看真实文书。）",
                "stage": "一审", "status": "draft", "created_at": None,
            }}
        try:
            doc = db.query(Document).filter(Document.id == doc_id).first()
            if not doc:
                return {"code": 404, "msg": "文书不存在", "data": None}
            return {
                "code": 200,
                "msg": "success",
                "data": {
                    "id": doc.id,
                    "case_type": doc.case_type,
                    "title": doc.title,
                    "content": doc.content,
                    "stage": doc.stage,
                    "status": doc.status,
                    "created_at": doc.created_at.isoformat() if doc.created_at else None,
                },
            }
        finally:
            db.close()


document_service = DocumentService()
