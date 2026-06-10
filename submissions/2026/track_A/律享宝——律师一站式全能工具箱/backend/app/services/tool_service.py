"""
法律工具智能编排服务
"""
from app.core.database import SessionLocal
from app.models.models import Tool, GenerationRecord
from app.agents.tool_agent import orchestrate_tools, TOOLS_CATALOG


class ToolService:
    """法律工具导航与编排"""

    def get_catalog(self) -> dict:
        """获取工具分类目录"""
        COLORS = ["#4F46E5", "#059669", "#D97706", "#DC2626", "#0891B2", "#7C3AED", "#DB2777", "#65A30D", "#0D9488", "#9333EA", "#2563EB"]
        color_idx = 0
        groups = {}
        for t in TOOLS_CATALOG:
            cat = t["category"]
            if cat not in groups:
                groups[cat] = []
            tags = t.get("tags", [])
            groups[cat].append({
                "id": len(groups[cat]),
                "name": t["name"],
                "desc": tags[0] if tags else "",
                "tags": tags,
                "color": COLORS[color_idx % len(COLORS)],
            })
            color_idx += 1
        catalog = [{"category": cat, "items": items} for cat, items in groups.items()]
        return {"code": 200, "msg": "success", "data": {"catalog": catalog}}

    def orchestrate(self, user_id: int, user_need: str) -> dict:
        """工具编排主流程"""
        try:
            result = orchestrate_tools(user_need)
            try:
                self._save_record(user_id, "tool", {"user_need": user_need}, result)
            except Exception:
                pass  # 无数据库时跳过保存
            return {"code": 200, "msg": "编排完成", "data": result}
        except Exception as e:
            return {"code": 500, "msg": f"编排失败: {str(e)}", "data": None}

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


tool_service = ToolService()
