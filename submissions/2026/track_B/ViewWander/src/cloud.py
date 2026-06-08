#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ViewWander · 云端后端（Google AI Studio 原生 Gemini API · gemma-4-26b-a4b-it）
==============================================================================

评审的快速复现路径：只要 pip（其实零依赖）+ 一把 AI Studio key,无需 Mac / 本地推理
环境即可跑通整套多模态接力。两段都是真·多模态调用（整张图 inlineData base64 + 文本
一次喂入,视觉文本在同一次前向里融合)。

⚠ 关键工程点：云端 Gemma 4 思考强制开、关不掉。原生 Gemini API 把思考放进
`thought: true` 的独立 part —— 本脚本遍历 parts 时 **skip 掉 thought part**,
干净只留正文。这是「让强制思考的大模型也能吐干净独白」的命门,而非靠 prompt 求它别想。

⚙ pick 用 Gemma 4 **原生函数调用**：导演通过 tools / toolConfig 强制调用 cast_personas
（personas 用 enum 锁死 17 个合法 id）,而非自由文本 + JSON 解析 —— 结构化输出从根上杜绝
瞎编人格、免疫 markdown 围栏崩溃。云端 26b 思考不可控使 FC pick 较慢（实测 ~110s）,故
timeout 给到 200s。

直接跑（也可经 main.py 交互选后端）：
    export GEMMA_API_KEY=<你的 AI Studio key>     # 或 GOOGLE_API_KEY
    python src/cloud.py                          # 默认分析 data/1.jpg
    python src/cloud.py data/7.jpg         # 指定一张图
    python src/cloud.py --all                    # 跑遍 data/ 全部 sample 图
获取 key：https://aistudio.google.com/apikey
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

# 允许 `python src/cloud.py` 直接跑（把 src/ 加入 import 路径）。
sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402
from common import Persona  # noqa: E402

# ── 配置 ────────────────────────────────────────────────────────────────────
# 云端 Gemma 4 经 Google AI Studio 的**原生 Gemini API** 托管访问。
NATIVE_API_BASE = "https://generativelanguage.googleapis.com/v1beta"
DEFAULT_MODEL = "gemma-4-26b-a4b-it"  # 26B MoE,与前端云端模式一致

# pick 思考方差大（实测 ~1300-1600 token）,给足头部空间,否则思考吃光额度、正文不出。
PICK_MAX_TOKENS = 4096
# voice 思考短得多（~300）,1024 足够覆盖思考 + 独白。
VOICE_MAX_TOKENS = 1024


# ── 鉴权 / 图片载体 ──────────────────────────────────────────────────────────
def _api_key() -> str:
    key = os.environ.get("GEMMA_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not key:
        sys.exit(
            "缺少 API key。请 `export GEMMA_API_KEY=<你的 AI Studio key>`。\n"
            "获取：https://aistudio.google.com/apikey"
        )
    return key


def encode_image(path: Path) -> dict[str, str]:
    """图片文件 → 原生 inlineData {mimeType, data(base64)}。这是多模态输入的载体。"""
    mime, b64 = common.read_image_b64(path)
    return {"mimeType": mime, "data": b64}


# ── 选角工具（原生 Gemini functionDeclarations · pick 用）──────────────────────
def build_cast_tool(personas: list[Persona]) -> dict:
    """导演的「选角工具」声明。personas 用 enum 锁死合法 id —— constrained decoding 从根上
    保证 args 只含合法人格,且天然免疫 freetext 的 markdown 围栏崩溃。"""
    return {
        "functionDeclarations": [{
            "name": common.CAST_TOOL_NAME,
            "description": common.CAST_TOOL_DESC,
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "personas": {
                        "type": "ARRAY",
                        "description": common.CAST_PERSONAS_DESC,
                        "items": {"type": "STRING", "enum": [p.id for p in personas]},
                        "minItems": 2,
                        "maxItems": 4,
                    },
                    "context": {
                        "type": "STRING",
                        "description": common.CAST_CONTEXT_DESC,
                    },
                },
                "required": ["personas", "context"],
            },
        }]
    }


# ── Gemma 4 调用（原生 Gemini API · 多模态 inlineData · skip thought part）─────
def _post(model: str, body: dict, timeout: int) -> dict:
    req = urllib.request.Request(
        f"{NATIVE_API_BASE}/models/{model}:generateContent",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json", "x-goog-api-key": _api_key()},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "ignore")
        sys.exit(f"Gemma 调用失败（HTTP {e.code}）：{detail}")
    except urllib.error.URLError as e:
        sys.exit(f"网络错误：{e.reason}")


def _call_gemma(model: str, system_prompt: str, user_text: str,
                inline_image: dict[str, str], max_tokens: int) -> str:
    """一次多模态 generateContent 调用,返回**非思考正文**（skip thought:true 的 part）。"""
    body = {
        "systemInstruction": {"parts": [{"text": system_prompt}]},
        "contents": [{
            "role": "user",
            # 图放文字前（model card 指引）,图 + 文本一次喂入 → 视觉文本融合。
            "parts": [{"inlineData": inline_image}, {"text": user_text}],
        }],
        "generationConfig": {"maxOutputTokens": max_tokens},
    }
    payload = _post(model, body, timeout=120)
    parts = (payload.get("candidates") or [{}])[0].get("content", {}).get("parts", [])
    # 关键：skip thought part —— 强制思考不进正文。
    text = "".join(
        p["text"] for p in parts
        if not p.get("thought") and isinstance(p.get("text"), str)
    ).strip()
    if not text:
        finish = (payload.get("candidates") or [{}])[0].get("finishReason", "?")
        sys.exit(f"模型只返回了思考、没有正文（finishReason={finish}）。试着调大 max_tokens。")
    return text


def _call_gemma_pick(model: str, system_prompt: str, inline_image: dict[str, str],
                     tool: dict, max_tokens: int) -> dict:
    """pick 专用：带 tools + toolConfig(强制 ANY) 的多模态调用,返回 cast_personas 的 args。
    云端 Gemma 思考强制开、FC 模式下 pick 思考更重（实测 ~110s）,故 timeout 给到 200s。"""
    body = {
        "systemInstruction": {"parts": [{"text": system_prompt}]},
        "contents": [{
            "role": "user",
            "parts": [{"inlineData": inline_image}, {"text": "分析这张图"}],
        }],
        "tools": [tool],
        "toolConfig": {"functionCallingConfig": {
            "mode": "ANY", "allowedFunctionNames": [common.CAST_TOOL_NAME],
        }},
        "generationConfig": {"maxOutputTokens": max_tokens},
    }
    payload = _post(model, body, timeout=200)
    parts = (payload.get("candidates") or [{}])[0].get("content", {}).get("parts", [])
    # 取 functionCall（skip thought:true 的思考 part）。
    for p in parts:
        fc = p.get("functionCall")
        if fc and fc.get("name") == common.CAST_TOOL_NAME:
            return fc.get("args") or {}
    finish = (payload.get("candidates") or [{}])[0].get("finishReason", "?")
    sys.exit(f"导演没走 functionCall（finishReason={finish}）。试着调大 max_tokens。")


# ── 后端契约实现（common.run_relay 通过这俩驱动）─────────────────────────────
def pick(personas: list[Persona], inline_image: dict[str, str],
         model: str) -> tuple[list[str], str]:
    """① 导演看图（**原生 function calling**）,返回 (原始人格 id 列表, 场景纸条)。"""
    args = _call_gemma_pick(model, common.build_pick_prompt(personas, "tool"),
                            inline_image, build_cast_tool(personas), PICK_MAX_TOKENS)
    return list(args.get("personas") or []), (args.get("context") or "")


def voice(persona: Persona, context: str,
          prior: list[tuple[str, str]], inline_image: dict[str, str],
          model: str) -> str:
    """② 单个人格就着图 + 场景 + 前文,说 1-2 句独白。"""
    return _call_gemma(model, persona.system_prompt,
                       common.build_user_message(persona, context, prior),
                       inline_image, VOICE_MAX_TOKENS)


# ── 独立运行入口 ─────────────────────────────────────────────────────────────
def run(image: str = "data/1.jpg", all_flag: bool = False,
        model: str | None = None) -> None:
    common.run_images(sys.modules[__name__], model, image, all_flag)


def main() -> None:
    ap = argparse.ArgumentParser(
        description="ViewWander · 云端 Gemma 4 多模态接力（Google AI Studio）",
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
