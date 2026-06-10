#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ViewWander · Gemma 4 多模态接力 · 交互入口（赛道 B · Multimodal）
================================================================

把《极乐迪斯科》式的内心独白塞进相机取景器：给一张图,让 Gemma 4 扮演一群住在脑子里的
「人格」,对画面**接力**吐内心独白。导演（原生 function calling）看图挑出被这帧强触发的
2-4 个人格 + 一句场景纸条,然后这几个人格各自就着图 + 前文说 1-2 句。

ViewWander 有两条后端,本入口让你运行时选：

  1) 云端 cloud（默认）—— Google AI Studio 原生 Gemini API · gemma-4-26b-a4b-it（26B MoE）
       评审快速路径：零依赖 + 一把 key 即可跑,无需 Mac / 本地推理环境。
  2) 本地 local        —— 本机 oMLX（OpenAI 兼容）· gemma-4-e4b-it-4bit（端侧 E4B）
       照片不出设备、断网也能跑；需 Apple Silicon + oMLX 常驻 8080。

用法
----
    python main.py                  # 交互：先问云端/本地,云端再问 key,然后选图开跑

也可直接跑某条后端、带命令行参数（跳过交互）：
    python src/cloud.py --all
    python src/local.py data/7.jpg

获取云端 key：https://aistudio.google.com/apikey
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# 把 src/ 加入 import 路径,加载两条后端。
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))


def _prompt(msg: str, default: str = "") -> str:
    """读一行输入；EOF（非交互管道）时回落到默认值,不崩。"""
    try:
        ans = input(msg).strip()
    except EOFError:
        return default
    return ans or default


def _choose_backend() -> str:
    print("ViewWander · 选择运行后端")
    print("  [1] 云端 cloud（默认）—— Google AI Studio · gemma-4-26b-a4b-it · 需 API key")
    print("  [2] 本地 local       —— 本机 oMLX · gemma-4-e4b-it-4bit · 需 oMLX 常驻 8080")
    while True:
        ans = _prompt("请选择 [1/2]（回车=1 云端）：", "1")
        if ans in ("1", "cloud", "云端"):
            return "cloud"
        if ans in ("2", "local", "本地"):
            return "local"
        print("  无效输入,请输入 1 或 2。")


def _ensure_cloud_key() -> None:
    """云端需要 key：环境已有就用,否则交互索取并写进环境,供 cloud 后端读取。"""
    if os.environ.get("GEMMA_API_KEY") or os.environ.get("GOOGLE_API_KEY"):
        print("  已检测到环境变量里的 API key,直接使用。")
        return
    print("  云端需要 Google AI Studio API key（申请：https://aistudio.google.com/apikey）")
    key = _prompt("  粘贴你的 key：")
    if not key:
        sys.exit("未提供 API key,无法走云端。可改选本地,或设置 GEMMA_API_KEY 后重试。")
    os.environ["GEMMA_API_KEY"] = key


def _choose_images() -> tuple[str, bool]:
    """选图：回车=默认首图,'all'=全图集,或一个具体路径。"""
    ans = _prompt(
        "\n选择要分析的图（回车=data/1.jpg · 输 all=全部 · 或填一个路径）：", ""
    )
    if ans.lower() == "all":
        return "", True
    return (ans or "data/1.jpg"), False


def main() -> None:
    backend_name = _choose_backend()

    if backend_name == "cloud":
        _ensure_cloud_key()
        import cloud as backend
    else:
        import local as backend

    image, all_flag = _choose_images()
    print(f"\n→ 后端：{backend_name} · 开跑\n")
    backend.run(image=image, all_flag=all_flag)


if __name__ == "__main__":
    main()
