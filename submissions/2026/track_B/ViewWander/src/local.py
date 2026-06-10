#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ViewWander · 端侧后端（本机 oMLX · OpenAI 兼容 · gemma-4-e4b-it-4bit）
=====================================================================

照片不出设备、断网也能跑 —— 这是 ViewWander「端侧 E4B」卖点的可运行硬证据。链路打的是
本机 **oMLX**（Mac 原生 MLX server · https://omlx.ai/ · 监听 localhost:8080 ·
OpenAI 兼容 `/v1/chat/completions`）,里面加载 `gemma-4-e4b-it-4bit`（4.5B 有效参数 ·
4bit · ~5GB · Apple Silicon unified memory 跑得宽松)。与前端 web/src/lib/viewwander-mlx.ts
同构。

端侧 e4b **不强制思考**,正文直接拿,无需云端那套 skip thought part —— 是云端那条路才有的
负担。pick 同样走**原生函数调用**（OpenAI `tools` / `tool_choice` 强制 cast_personas
+ enum 锁 17 id + temp=0）；e4b 走 oMLX 的 tool 模式比云端快得多（实测 pick ~3s）。

前置条件（评审复现门槛比云端高,见技术报告 §2)：
    - Apple Silicon Mac
    - 装 oMLX 并常驻 8080：见 https://omlx.ai/
    - 加载模型 gemma-4-e4b-it-4bit（~5GB）

直接跑（也可经 main.py 交互选后端）：
    python src/local.py                          # 默认分析 data/1.jpg
    python src/local.py data/7.jpg         # 指定一张图
    python src/local.py --all                    # 跑遍 data/ 全部 sample 图
不需要任何 API key、不联网。
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

# 允许 `python src/local.py` 直接跑（把 src/ 加入 import 路径）。
sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402
from common import Persona  # noqa: E402

# ── 配置 ────────────────────────────────────────────────────────────────────
# 本机 oMLX 的 OpenAI 兼容端点。鉴权用本地占位 token（oMLX 不校验,只要带）。
BASE_URL = "http://localhost:8080/v1/chat/completions"
API_KEY = "local"
DEFAULT_MODEL = "gemma-4-e4b-it-4bit"  # 端侧 E4B,与前端本机模式一致

# e4b 不强制思考,token 预算可比云端小得多。
PICK_MAX_TOKENS = 500
VOICE_MAX_TOKENS = 150


# ── 图片载体（OpenAI 兼容 image_url：data URL）────────────────────────────────
def encode_image(path: Path) -> str:
    """图片文件 → OpenAI image_url 的 data URL（base64）。这是多模态输入的载体。"""
    mime, b64 = common.read_image_b64(path)
    return f"data:{mime};base64,{b64}"


# ── 选角工具（OpenAI 兼容 tools · pick 用）─────────────────────────────────────
def build_cast_tool(personas: list[Persona]) -> dict:
    """导演的「选角工具」声明（OpenAI 兼容）。personas 用 enum 锁死合法 id —— constrained
    decoding 从根上保证 args 只含合法人格,免疫 freetext 的 markdown 围栏崩溃。"""
    return {
        "type": "function",
        "function": {
            "name": common.CAST_TOOL_NAME,
            "description": common.CAST_TOOL_DESC,
            "parameters": {
                "type": "object",
                "properties": {
                    "personas": {
                        "type": "array",
                        "description": common.CAST_PERSONAS_DESC,
                        "items": {"type": "string", "enum": [p.id for p in personas]},
                        "minItems": 2,
                        "maxItems": 4,
                    },
                    "context": {
                        "type": "string",
                        "description": common.CAST_CONTEXT_DESC,
                    },
                },
                "required": ["personas", "context"],
            },
        },
    }


# ── oMLX 调用（OpenAI 兼容 · 多模态 image_url · e4b 无强制思考）─────────────────
def _post(body: dict, timeout: int) -> dict:
    req = urllib.request.Request(
        BASE_URL,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json",
                 "Authorization": f"Bearer {API_KEY}"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "ignore")
        sys.exit(f"oMLX 调用失败（HTTP {e.code}）：{detail}")
    except urllib.error.URLError as e:
        sys.exit(
            f"连不上本机 oMLX（{e.reason}）。请确认 oMLX 已常驻 8080 且已加载 "
            f"{DEFAULT_MODEL}。安装见 https://omlx.ai/"
        )


def _call_local(system_prompt: str, user_text: str,
                data_url: str, max_tokens: int, model: str) -> str:
    """一次多模态 chat/completions 调用,返回正文（e4b 无强制思考,content 即正文）。"""
    body = {
        "model": model,
        "stream": False,
        "max_tokens": max_tokens,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": [
                {"type": "text", "text": user_text},
                {"type": "image_url", "image_url": {"url": data_url}},
            ]},
        ],
    }
    payload = _post(body, timeout=120)
    text = ((payload.get("choices") or [{}])[0]
            .get("message", {}).get("content") or "").strip()
    if not text:
        sys.exit("模型没返回正文。试着调大 max_tokens 或检查 oMLX 日志。")
    return text


def _call_local_pick(system_prompt: str, data_url: str,
                     tool: dict, max_tokens: int, model: str) -> dict:
    """pick 专用：带 tools + tool_choice(强制 cast_personas) 的多模态调用,返回 args dict。
    选人结果在 tool_calls 的 arguments（JSON 串）,**不在 content**（oMLX tool 模式会把
    <eos> 泄漏进 content,绝不能读它）。"""
    body = {
        "model": model,
        "stream": False,
        "max_tokens": max_tokens,
        # pick 用贪心解码：eval 实测 temp=0 选人稳定可预期、质量最优。
        "temperature": 0,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": [
                {"type": "text", "text": "分析这张图"},
                {"type": "image_url", "image_url": {"url": data_url}},
            ]},
        ],
        "tools": [tool],
        "tool_choice": {"type": "function",
                        "function": {"name": common.CAST_TOOL_NAME}},
    }
    payload = _post(body, timeout=120)
    tool_calls = ((payload.get("choices") or [{}])[0]
                  .get("message", {}).get("tool_calls") or [])
    for c in tool_calls:
        fn = c.get("function") or {}
        if fn.get("name") == common.CAST_TOOL_NAME:
            try:
                return json.loads(fn.get("arguments") or "{}")
            except json.JSONDecodeError:
                sys.exit(f"cast_personas 的 arguments 不是合法 JSON：{fn.get('arguments')}")
    sys.exit("导演没走 tool_call（无 cast_personas）。检查 oMLX 是否支持 tool_choice。")


# ── 后端契约实现（common.run_relay 通过这俩驱动）─────────────────────────────
def pick(personas: list[Persona], data_url: str,
         model: str) -> tuple[list[str], str]:
    """① 导演看图（**原生 function calling**）,返回 (原始人格 id 列表, 场景纸条)。"""
    args = _call_local_pick(common.build_pick_prompt(personas, "tool"), data_url,
                            build_cast_tool(personas), PICK_MAX_TOKENS, model)
    return list(args.get("personas") or []), (args.get("context") or "")


def voice(persona: Persona, context: str,
          prior: list[tuple[str, str]], data_url: str,
          model: str) -> str:
    """② 单个人格就着图 + 场景 + 前文,说 1-2 句独白。"""
    return _call_local(persona.system_prompt,
                       common.build_user_message(persona, context, prior),
                       data_url, VOICE_MAX_TOKENS, model)


# ── 独立运行入口 ─────────────────────────────────────────────────────────────
def run(image: str = "data/1.jpg", all_flag: bool = False,
        model: str | None = None) -> None:
    common.run_images(sys.modules[__name__], model, image, all_flag)


def main() -> None:
    ap = argparse.ArgumentParser(
        description="ViewWander · 端侧 Gemma 4 多模态接力（本机 oMLX）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("image", nargs="?", default="data/1.jpg",
                    help="要分析的图片路径（默认 data/1.jpg）")
    ap.add_argument("--all", action="store_true",
                    help="分析 data/ 下全部 sample 图")
    ap.add_argument("--model", default=DEFAULT_MODEL,
                    help=f"Gemma 4 模型 id（默认 {DEFAULT_MODEL}）")
    args = ap.parse_args()
    run(args.image, args.all, args.model)


if __name__ == "__main__":
    main()
