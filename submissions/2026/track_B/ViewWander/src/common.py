#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ViewWander · 两条后端共享的核心逻辑（人格名册 / 导演 prompt / 接力编排）
======================================================================

云端（src/cloud.py）与本地（src/local.py）两条后端**只有最底层那次 HTTP
请求的形状不同**（原生 Gemini API vs OpenAI 兼容、26B 云端 vs e4b 端侧）；人格名册、
导演 prompt、两段式接力编排都一模一样 —— 全部收在这里，单一事实源。

后端只需实现一个「极薄」契约（duck typing，无需继承）：

    backend.DEFAULT_MODEL                       -> str
    backend.encode_image(path: Path)            -> blob   # 后端自己的图片载体（opaque）
    backend.pick(personas, blob, model)         -> (raw_ids: list[str], context: str)
    backend.voice(persona, context, prior, blob, model) -> str

选人结果的「校验 + 去重 + 按 order 重排 + 截断 ≤4」是共享逻辑（finalize_pick），
两条后端都复用，保证接力韵律一致（本能→智力→社会→超现实）。
"""

from __future__ import annotations

import base64
import mimetypes
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

# 资产根（src/ 自己,即本文件所在目录）—— personas/ 和 data/ 都在这。
ASSETS_ROOT = Path(__file__).resolve().parent


# ── 人格名册：从 markdown 事实源解析（与前端共用同一批 *.md）───────────────────
@dataclass
class Persona:
    id: str
    english_name: str
    order: int
    trigger: str          # 「什么样的画面会击中我」——导演选人用
    system_prompt: str     # 该人格独白时的声口 system prompt（md 正文）


def _find_personas_dir() -> Path:
    """人格 md 的事实源目录。优先提交目录的 personas/，回落到前端 web/src/personas/。"""
    for cand in (
        ASSETS_ROOT / "personas",
        ASSETS_ROOT / "web" / "src" / "personas",
    ):
        if cand.is_dir():
            return cand
    sys.exit(
        "找不到人格名册目录（personas/ 或 web/src/personas/）。"
        "请在提交目录根运行 main.py。"
    )


def _parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    """解析 `--- key: value --- 正文` 形式的 markdown。值都在一行内,无需 YAML 库。"""
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", text, re.DOTALL)
    if not m:
        return {}, text
    meta: dict[str, str] = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    return meta, m.group(2).strip()


def load_personas() -> list[Persona]:
    """读全部人格 md,按 order 升序返回（= 接力顺序:本能→智力→社会→超现实）。"""
    personas: list[Persona] = []
    for md in sorted(_find_personas_dir().glob("*.md")):
        if md.name.startswith("_") or md.name == "README.md":
            continue
        meta, body = _parse_frontmatter(md.read_text(encoding="utf-8"))
        if not meta.get("id"):
            continue
        personas.append(
            Persona(
                id=meta["id"],
                english_name=meta.get("englishName", meta["id"]),
                order=int(meta.get("order", "999")),
                trigger=meta.get("trigger", ""),
                system_prompt=body,
            )
        )
    personas.sort(key=lambda p: p.order)
    if not personas:
        sys.exit("人格名册为空,无法运行。")
    return personas


# ── Prompt 构造（移植自前端 web/src/lib/personas.ts）──────────────────────────
def build_pick_prompt(personas: list[Persona], output_mode: str = "tool") -> str:
    """导演 system prompt —— 遍历名册把各人格 trigger 动态拼进去（单一事实源）。
    output_mode='tool' 去掉「返回 JSON」尾巴、改由 function calling 提交 —— JSON 指令会和
    tool 抢方向盘,模型转去吐文本而非走 functionCall（实测确认）。两条后端的 pick 都走 FC,
    故默认 'tool'。"""
    roster = "\n".join(f"- **{p.id}**（{p.english_name}）：{p.trigger}" for p in personas)
    enum_list = " / ".join(f'"{p.id}"' for p in personas)
    head = f"""你是这套《极乐迪斯科》式内心独白系统背后的**导演**。

设定：你是个看过几百上千部电影的影迷 nerd。平时沉默寡言、表情严肃,话少到近乎冷淡——但你的脑子一刻没停,每看一个画面都在心里偷偷开小剧场：给它配光、想它是哪部片的某一帧、谁该在这一格里开口。

你的工作分两步。

**第一步 · 挑声音（沉默而挑剔）**
画面前有 {len(personas)} 个可调用的声音。你不是 DJ,不会把每个声音都推上台——大多数随手拍的照片只配得上一两个声音开口。**宁缺毋滥：只召唤被这张图"真正、强烈"击中的声音；没被强触发的,宁可不选,也不要凑数。** 通常 2 个就够,只有画面信息真的丰富时才上到 3-4 个。

每个声音各自被什么样的画面"击中"——每条都写明了它问的问题/它的尺度/它的输入条件,**职责相邻的几个别互相串台,按各自的边界分**：

{roster}

凭你影迷的眼睛判断这张图真正击中了哪几个,召它们上台；其余的留在后台。

**第二步 · 写 context（你藏不住的那点内心戏）**
表面你只是淡淡记一句,但这是你内心小剧场唯一漏出来的地方。用一句中文（15-40 字）写下这张图最耐人寻味的氛围 + 主体动作 + 那个让你"咦"一下的钩子。带一点你影迷的眼睛,但别写成影评、别报片名——这是你递给后面那几个声音的一张纸条。"""

    # tool 模式：选人逻辑同上,只把输出契约换成 function call。**绝不保留"返回 JSON"指令**
    # —— 它会和 tool 抢方向盘,模型转去吐文本而非走 functionCall。enum 约束由 tool schema
    # 的 parameters 强制,prompt 里无需重复 id 列表。
    if output_mode == "tool":
        return head + (
            "\n\n挑好声音、想好那句 context 后,**调用 cast_personas 工具**提交："
            "personas 放被这张图真正击中的 2-4 个声音的 id,context 放你那张纸条"
            "（15-40 字中文）。直接调用工具,不要用文字回答。"
        )

    return head + f"""

返回严格 JSON（**只有 JSON：不许 markdown 围栏、不许解释、不许任何多余字符**——你沉默,记得吗）：

{{
  "personas": [...],     // 字符串数组,元素只能是 {enum_list}（英文 id,不要中文）。**至少 2 个、至多 4 个**,只放被真正击中的那几个。
  "context": "..."        // 一句中文（15-40 字）,氛围 + 主体动作 + 最耐人寻味的钩子。供后续接力的声音共享参考。
}}

只返回 JSON,不要其他任何字符。"""


def build_user_message(persona: Persona, context: str,
                       prior_voices: list[tuple[str, str]]) -> str:
    """人格接力的 user message。前文已说的内容作为 [前文已有] 前缀塞入 —— 接力感来自这里。"""
    if not prior_voices:
        return f"[场景] {context}\n\n请按你的视角,看这张图,说 1-2 句（20-50 字）。"
    prior_lines = "\n".join(f"{name}: {text}" for name, text in prior_voices)
    return "\n".join([
        f"[场景] {context}",
        "",
        "[前文已有]",
        prior_lines,
        "",
        f"现在轮到你（{persona.english_name}）。不要重复前文已经说过的具体物件或角度。",
        "补上**属于你那一面** —— 你的视角、你的语调。可以隐性回应,但不要明引。",
    ])


# ── 选角工具的共享元信息（两条后端各自包成自己的 wire 格式）────────────────────
# 云端原生 Gemini 用大写类型 + functionDeclarations；本地 OpenAI 兼容用小写 + type:function。
# 形状不同,但名字/描述/enum/min-max 一致 —— 收在这做单一事实源。
CAST_TOOL_NAME = "cast_personas"
CAST_TOOL_DESC = "召唤被这一帧画面强烈击中的 2-4 个人格,并附一句导演的内心独白纸条。"
CAST_PERSONAS_DESC = "被强触发的人格 id（宁缺毋滥,只放被真正击中的）"
CAST_CONTEXT_DESC = "一句导演的内心独白纸条（15-40 字中文）"


# ── 图片读取（两条后端共享 base64 编码,只是最终包装不同）──────────────────────
def read_image_b64(path: Path) -> tuple[str, str]:
    """图片文件 → (mimeType, base64 字符串)。云端包成 inlineData、本地包成 data URL。"""
    mime = mimetypes.guess_type(str(path))[0] or "image/jpeg"
    b64 = base64.b64encode(path.read_bytes()).decode("ascii")
    return mime, b64


# ── 选人结果定型：校验 + 去重 + 按 order 重排 + 截断（两条后端共享）──────────────
def finalize_pick(personas: list[Persona], raw_ids: list[str],
                  context: str) -> tuple[list[Persona], str]:
    """后端 pick 交回原始 id 列表 + context,这里统一定型成接力 lineup。
    保证：① 只留合法 id；② ≥2 个否则报错；③ 按名册 order 升序（接力韵律）；④ 最多 4 个。"""
    by_id = {p.id: p for p in personas}
    picked = [pid for pid in raw_ids if pid in by_id]
    if len(picked) < 2:
        sys.exit(f"导演只选了 {len(picked)} 个有效人格（需 ≥2）。原始：{raw_ids}")
    lineup = sorted((by_id[pid] for pid in dict.fromkeys(picked)),
                    key=lambda p: p.order)[:4]
    ctx = (context or "画面里有值得观察的细节").strip()
    return lineup, ctx


# ── 后端契约（仅作类型提示,后端无需继承）─────────────────────────────────────
class Backend(Protocol):
    DEFAULT_MODEL: str

    def encode_image(self, path: Path):  # -> opaque blob
        ...

    def pick(self, personas: list[Persona], blob,
             model: str) -> tuple[list[str], str]:
        ...

    def voice(self, persona: Persona, context: str,
              prior: list[tuple[str, str]], blob, model: str) -> str:
        ...


# ── 一张图的完整接力（编排共享,后端只管那次 HTTP）────────────────────────────
def run_relay(backend: Backend, personas: list[Persona],
              image_path: Path, model: str) -> None:
    print(f"\n{'═' * 64}")
    print(f"📷  {image_path.name}")
    print("═" * 64)

    blob = backend.encode_image(image_path)

    print("\n🎬  导演看图选人格 …")
    raw_ids, raw_ctx = backend.pick(personas, blob, model)
    lineup, context = finalize_pick(personas, raw_ids, raw_ctx)
    print(f'    场景纸条：「{context}」')
    print(f'    点亮：{" → ".join(p.english_name for p in lineup)}\n')

    prior: list[tuple[str, str]] = []
    for persona in lineup:
        voice = backend.voice(persona, context, prior, blob, model)
        print(f"  〔{persona.english_name}〕 {voice}\n")
        prior.append((persona.english_name, voice))


def resolve_images(image: str, all_flag: bool) -> list[Path]:
    """把命令行/交互输入的图片选择解析成实际文件列表。"""
    if all_flag:
        images = sorted((ASSETS_ROOT / "data").glob("*.jpg"))
        if not images:
            sys.exit("data/ 下没有 .jpg sample 图。")
        return images
    p = Path(image)
    if not p.is_absolute():
        p = ASSETS_ROOT / p
    if not p.is_file():
        sys.exit(f"图片不存在：{p}")
    return [p]


def run_images(backend: Backend, model: str | None,
               image: str = "data/1.jpg", all_flag: bool = False) -> None:
    """后端的统一入口：加载名册 → 解析图片 → 逐张跑接力。"""
    model = model or backend.DEFAULT_MODEL
    personas = load_personas()
    print(f"已加载 {len(personas)} 个人格名册 · 模型 {model}")
    for img in resolve_images(image, all_flag):
        run_relay(backend, personas, img, model)
