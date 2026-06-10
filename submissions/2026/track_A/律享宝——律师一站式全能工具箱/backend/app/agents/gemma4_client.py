"""
Google Gemma 4 AI 模型集成服务
通过 OpenAI 兼容接口调用 Gemma 4（支持 GMI Cloud / Google AI Studio / 本地部署等）
Gemma 4 是 Google 开源大语言模型，本项目用于 Google Gemma 4 开发大赛
"""
import json
import time
from typing import Optional, Callable, Any
from openai import OpenAI
from app.core.config import GEMMA4_API_KEY, GEMMA4_BASE_URL, GEMMA4_MODEL


class Gemma4Client:
    """Google Gemma 4 客户端封装（可切换模拟模式与真实 Gemma 4 API）"""

    def __init__(self, model: str = GEMMA4_MODEL, use_mock: bool = True):
        self.model = model
        self.use_mock = use_mock
        self.functions_registry = {}

    def register_function(self, name: str, func: Callable, description: str = ""):
        """注册工具函数供模型原生函数调用"""
        self.functions_registry[name] = {
            "function": func,
            "description": description,
        }

    def _build_prompt(self, system_prompt: str, user_input: str, functions: list = None) -> dict:
        """构建模型请求 payload"""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input},
        ]
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.3,
            "max_tokens": 8192,
            "top_p": 0.95,
        }
        if functions:
            payload["tools"] = functions
        return payload

    def _call_mock(self, payload: dict) -> dict:
        """模拟 Gemma 4 模型响应（开发/演示用）"""
        time.sleep(0.5)  # 模拟延迟
        return {
            "content": "（Gemma 4 模拟响应）功能开发完成后，此处将返回 Google Gemma 4 模型的实际生成结果。\n\n## 生成结果\n\n根据您提供的案件信息，已为您生成以下文书内容...",
            "tokens_used": 256,
            "latency_ms": 500,
        }

    def _call_gemma4_api(self, payload: dict) -> dict:
        """调用 Google Gemma 4 API（OpenAI 兼容接口）"""
        try:
            client = OpenAI(
                api_key=GEMMA4_API_KEY,
                base_url=GEMMA4_BASE_URL,
            )

            # 提取消息和参数
            kwargs = {k: v for k, v in payload.items() if k != "model"}
            response = client.chat.completions.create(
                model=self.model,
                **kwargs,
            )

            content = response.choices[0].message.content or ""

            return {
                "content": content,
                "tokens_used": response.usage.total_tokens if response.usage else 0,
                "latency_ms": 0,
            }
        except Exception as e:
            return {"content": f"API 调用错误: {str(e)}", "tokens_used": 0, "latency_ms": 0}

    def generate(self, system_prompt: str, user_input: str, functions: list = None) -> dict:
        """生成内容"""
        payload = self._build_prompt(system_prompt, user_input, functions)
        start = time.time()

        if self.use_mock:
            result = self._call_mock(payload)
        else:
            result = self._call_gemma4_api(payload)

        elapsed = int((time.time() - start) * 1000)

        return {
            "content": result["content"],
            "tokens_used": result.get("tokens_used", 0),
            "latency_ms": result.get("latency_ms", elapsed),
        }

    def generate_structured(self, system_prompt: str, user_input: str, output_schema: dict) -> dict:
        """生成结构化输出（JSON）"""
        format_instruction = f"""
请严格按照以下 JSON Schema 输出结果，不包含额外说明：
```json
{json.dumps(output_schema, ensure_ascii=False, indent=2)}
```
"""
        result = self.generate(system_prompt, user_input + "\n\n" + format_instruction)
        # 尝试从结果中提取 JSON
        content = result["content"]
        try:
            # 提取 JSON 块
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                json_str = content.split("```")[1].strip()
            else:
                json_str = content
            parsed = json.loads(json_str)
            result["parsed"] = parsed
        except (json.JSONDecodeError, IndexError):
            result["parsed"] = {"raw": content}
        return result

    def function_call_iteration(self, system_prompt: str, user_input: str, functions: list) -> dict:
        """多步函数调用：模型自动决定调用哪些工具并整合结果"""
        step_results = []
        current_input = user_input

        for step in range(1, 6):  # 最多 5 步
            result = self.generate(system_prompt, current_input, functions)

            # 检查是否包含函数调用标记
            content = result["content"]
            step_results.append({"step": step, "output": content})

            # 模拟中直接返回（实际部署时由模型决定是否继续）
            break

        return {
            "final_content": step_results[-1]["output"] if step_results else "",
            "steps": step_results,
            "total_tokens": sum(r.get("tokens_used", 0) for r in step_results),
        }


# 全局单例
gemma_client = Gemma4Client(use_mock=True)
