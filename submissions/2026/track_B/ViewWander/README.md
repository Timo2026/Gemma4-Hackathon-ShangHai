# ViewWander · 取景器中的游戏旁白

队伍：GingerBeer  
赛道：B · Multimodal  
灵感：《极乐迪斯科》多人格 skill checks 与《Life is Strange: Before the Storm》的观景台脑补  

## 项目介绍

ViewWander 是一个相机应用。按一次快门，拍下取景器里的一帧画面，Gemma 4 会扮演一组住在脑子里的人格，对这帧画面**接力**吐出内心独白——逻辑看到几何与因果，本能看到威胁与生存，超现实人格看到诗意与神秘。**一张图 → 多种内在声音的并置**。

它针对的不是“这是什么”的识别问题，而是“这一帧让人联想到什么”的表达问题：常见相机应用的视觉理解止于贴标签、报物体，ViewWander 把它推进到主观解读与情绪投射这一层。一项贯穿全局的设计约束是——模型始终接收完整的 3:4 帧，而用户只看到居中的 1:1 方格，人格所解读的内容刻意包含取景框之外的部分，“画外之意”是本项目的核心设计意图。

落地上，导演（一次推理）看图从 17 人格池中挑出被该帧强触发的 2–4 个，随后这些人格各自看图、读前文，接力生成独白。系统提供端侧（本机 oMLX · Gemma `e4b`，照片不离设备）与云端（Google AI Studio · Gemma `26b` MoE，零环境可访问）两条后端，共用同一套编排核心。

## 链接

- **在线体验**：[view-wander.iwen-z.com](https://view-wander.iwen-z.com/)（打开即用，无需本地环境）
- **技术报告**：[`docs/tech-report.md`](./docs/tech-report.md)（模型选型 · 系统架构 · 多模态处理 · 对 Gemma 4 原生能力的运用 · 选人质量评测）
- **演示视频**：[`docs/demo-screen-recording.mp4`](./docs/demo-screen-recording.mp4)（1:05）
- **核心代码**：[`src/`](./src/)（`main.py` 入口 · `common.py` 共享编排 · `cloud.py` / `local.py` 双后端）
- **测试数据**：[`src/data/`](./src/data/)（14 张测试图与人工标注 `labels.jsonl`）
- **人格名册**：[`src/personas/`](./src/personas/)（17 个人格的声口 prompt 与触发边界）

## 本地运行

```bash
pip install -r requirements.txt   # 零第三方依赖
python main.py                    # 交互选云端或本地，云端粘贴 AI Studio key 后选图运行
```

云端 key 申请：https://aistudio.google.com/apikey 。完整运行说明（直接运行某条后端、命令行参数等）见[技术报告](./docs/tech-report.md) §7。
