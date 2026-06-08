# CareMind

**赛道 C：Edge AI / Android 端侧失智症家庭照护助手**

CareMind 是一款面向失智症家庭照护者的 AI Care Agent。它帮助家属把混乱、零散、情绪化的照护记录，整理成可追踪的照护线索、今晚可执行的小行动、低冲突沟通话术，以及复诊时可以复制给医生的摘要。

CareMind 不诊断、不处方、不判断是否需要检查，也不替代医生。C 赛道提交重点展示：**敏感照护记录可在 Android 真机上优先通过本地 Gemma LiteRT 模型处理**，让隐私数据更靠近家属自己的设备。

## 团队成员

CareMind Team：张媛、连婕妤、刘畅、郭鸿宇

## 评审快速入口

| 评审想看 | 入口 |
|---|---|
| 公开视频 | [Bilibili BV1hFEg6ZEVb](https://www.bilibili.com/video/BV1hFEg6ZEVb) |
| 主项目仓库 | [hyczy0809/CareMind](https://github.com/hyczy0809/CareMind) |
| 演示后端 | [https://caremind-1039168666325.us-west1.run.app](https://caremind-1039168666325.us-west1.run.app) |
| Android 安装包 | 由 `frontend/android` 基于上面的后端地址构建 |
| C 赛道核心代码 | `source/frontend/android/app/src/main/java/com/caremind/app/gemma/`、`source/frontend/lib/inference/local/`、`source/backend/my_agent/` |

建议先看 1 分钟视频，再看下方 Edge AI、Docker 和 Tool Calling 说明。视频文件不提交到 Git 历史中，README 使用可点击预览图链接到公开视频。

<p align="center">
  <a href="https://www.bilibili.com/video/BV1hFEg6ZEVb">
    <img src="docs/caremind-demo-video-preview.png" alt="CareMind demo video preview" width="860" />
  </a>
</p>

## 阅读路径

| 如果你想确认 | 建议阅读 |
|---|---|
| 是否符合 C 赛道 | [Edge AI 方案概览](#edge-ai-方案概览)、[硬件演示说明](#硬件演示说明) |
| 是否真的有端侧模型路径 | [模型选择](#模型选择)、`source/frontend/android/app/src/main/java/com/caremind/app/gemma/` |
| 是否有 Native Function Calling / Tool Calling | [Gemma 特性对齐](#gemma-特性对齐)、[Native Function Calling / Tool Calling 路径](#native-function-calling--tool-calling-路径) |
| 是否能启动后端 | [快速启动](#快速启动)、[Docker 启动后端](#docker-启动后端) |
| 是否有隐私和医疗边界 | [隐私与安全边界](#隐私与安全边界) |

## Edge AI 方案概览

```text
敏感照护记录输入到 Android 手机
-> 用户打开隐私模式
-> App 加载已下载的 Gemma LiteRT 模型
-> 本地完成照护记录理解 / 建议生成
-> 云端 Agent 作为非隐私场景下的完整工作流增强
```

本次提交包含 Android Native Bridge、模型下载器、模型生命周期管理、本地 inference router、XML prompt/parser 路径，以及 Cloud Run 模型目录接口。

## 模型选择

CareMind 的端侧路径支持 `.litertlm` / `.task` 格式的 Gemma-family 模型文件，使用同一套 Android LiteRT 集成方式。

| 模型 | 用途 | 说明 |
|---|---|---|
| Gemma 4 E2B / E4B LiteRT | 更大规格候选模型 | 通过动态模型目录和 Android 下载/加载路径支持；能否流畅运行取决于设备内存。 |
| Gemma 3 1B LiteRT | 当前硬件演示备用模型 | 约 557 MB，更适合普通 Android 手机，能降低 OOM 和闪退风险。 |

APK 不硬编码模型列表。App 会调用：

```http
GET /api/models
```

Cloud Run 后端会扫描 Google Cloud Storage 指定目录，返回其中所有 `.litertlm` 或 `.task` 文件。之后只要把 Gemma 4 E2B/E4B 文件放入 bucket，App 的模型选择器就能刷新看到，不需要重新打包 APK。

## Gemma 特性对齐

官方技术要求中提到 Native Function Calling、多模态处理和 Edge AI 部署。CareMind 本次提交的核心技术贡献是：**Gemma 在 Android 端侧的 Edge AI 部署**。

已经实现的部分：

- Android 原生模块管理 Gemma-family LiteRT 模型生命周期：下载、检查就绪状态、初始化 engine、释放 engine、文本生成，以及音频感知生成接口预留。
- Cloud Run + Google Cloud Storage 动态模型目录，使 Gemma 4 E2B/E4B LiteRT 候选模型可以在不重打包 APK 的情况下加入模型列表。
- 隐私模式 inference router，根据场景决定敏感记录留在本机处理，还是走云端完整 Agent 工作流。
- 本地 Gemma 输出采用结构化 XML contract，并通过 parser 转成产品数据；若模型输出不完整，则降级到确定性 fallback。
- 本地 guardrail、照护工作流、复诊摘要模块会把模型输出转成 typed product data，而不是直接展示一段聊天文本。
- 云端 ADK Agent 路径包含真实的 tool/function declarations。`cloud_agents.py` 定义照护工具、Memory 工具和 specialist agents；`cloudflare_openai_model.py` 会把这些声明转成 OpenAI-compatible `tools` / `tool_choice: auto` 请求，并把模型返回的 `tool_calls` 转回 ADK function calls 执行。

边界说明：

- C 赛道主路径是 Android Edge AI。离线 LiteRT 路径使用本地生成 + 结构化输出 contract，因为这是端侧隐私处理更可靠的方式。
- Native Function Calling 展示在可选的云端 Agent 路径中，不是离线 LiteRT 路径。
- 语音输入当前通过 Android 系统语音识别先转成可编辑文本；完全本地的音频转写是后续扩展方向。

简而言之，CareMind 不是简单 prompt 工程：端侧路径包含模型管理、隐私路由、结构化解析、安全边界和真机演示；云端路径则展示了完整的 function/tool calling Agent 编排。

## 硬件演示说明

### 硬件

- Android 手机
- 推荐 Android 8.0+
- 1B 演示模型建议至少 4 GB RAM
- Gemma 4 E2B/E4B LiteRT 实验建议使用更高内存设备

### Android 编译环境

- Expo SDK 52
- React Native 0.76
- Android compileSdk 35
- Android minSdk 24
- Kotlin / Gradle 使用 Expo Android 工程配置
- 推荐 JDK 17
- MediaPipe GenAI runtime：`com.google.mediapipe:tasks-genai:0.10.35`

本项目不涉及树莓派、MCU、自定义内核模块或底层驱动。硬件目标是标准 Android 手机。

### 硬件演示步骤

1. 在 Android 手机上安装 CareMind APK。
2. 打开 **Settings / Privacy Mode**。
3. 刷新模型目录。
4. 从后端下载 LiteRT 模型。
5. 关闭 Wi-Fi 和移动网络。
6. 输入一条敏感照护记录：

```text
外婆夜里醒了四次，一直说有人偷钱，晚饭只吃了几口，妈妈也很累。
```

7. 展示 CareMind 在本地返回非诊断性的照护观察和低负担行动建议。

建议视频字幕：

```text
Network off. Gemma LiteRT runs on the Android device for local care-note understanding.
```

## 提交目录结构

```text
CareMind/
├── README.md
├── TECHNICAL_REPORT.md
├── EDGE_HARDWARE_DEMO.md
├── requirements.txt
├── docs/
│   ├── caremind-demo-video-preview.png
│   ├── demo_storyboard.md
│   └── recording_guide.md
└── source/
    ├── backend/
    │   ├── main.py
    │   ├── openai_compat.py
    │   ├── my_agent/
    │   ├── requirements.txt
    │   ├── Dockerfile
    │   └── .env.example
    └── frontend/
        ├── app.json
        ├── package.json
        ├── lib/inference/
        ├── lib/speech/android-speech.ts
        └── android/
```

完整产品代码见主项目仓库。本提交目录只保留与 C 赛道评审相关的核心源码，方便快速检查端侧路径。

## 快速启动

### 后端本地启动

```bash
cd source/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --host 127.0.0.1 --port 8090
```

### Docker 启动后端

本提交包含后端 `Dockerfile`。从提交目录执行：

```bash
cd source/backend
cp .env.example .env
```

如果本地评审环境没有云端凭据，后端仍可以启动，并暴露 health 与模型 metadata 接口。构建并运行：

```bash
docker build -t caremind-backend .
docker run --rm \
  --env-file .env \
  -e PORT=8080 \
  -p 8080:8080 \
  caremind-backend
```

冒烟测试：

```bash
curl http://127.0.0.1:8080/health
curl http://127.0.0.1:8080/api/models
```

如需使用完整的托管模型目录流程，请在 `.env` 中配置：

```env
CAREMIND_GCS_MODEL_BUCKET=caremind-498713-models-asia
CAREMIND_GCS_MODEL_PREFIX=models
CAREMIND_GCS_DYNAMIC_CATALOG=1
CAREMIND_GCS_MODEL_DELIVERY=redirect
```

当前生产演示后端部署在 Cloud Run：

```text
https://caremind-1039168666325.us-west1.run.app
```

常用接口：

```http
GET  /health
GET  /api/models
GET  /api/models/{filename}/meta
GET  /api/models/{filename}
POST /api/care-workflow
POST /api/reports/follow-up
POST /v1/chat/completions
```

### Native Function Calling / Tool Calling 路径

后端也提供 OpenAI-compatible Agent 接口：

```http
POST /v1/chat/completions
```

当 ADK 依赖可用时，该接口会运行 `caremind_cloud_root_agent`。这个 Agent 配置了真实工具，例如：

- `run_cloud_care_workflow`
- `extract_care_signals`
- `assess_patient_risk`
- `assess_caregiver_burden`
- `create_care_plan`
- `retrieve_patient_profile`
- `retrieve_recent_events`
- `retrieve_behavior_baseline`
- `generate_doctor_summary`

`source/backend/my_agent/cloudflare_openai_model.py` 会把 ADK function declarations 转成 OpenAI-compatible `tools`，并发送 `tool_choice: auto`。当模型返回 `tool_calls` 时，adapter 会把它们转回 ADK function calls，让后端执行对应 Python 工具。

最小请求示例：

```bash
curl -X POST http://127.0.0.1:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "X-Session-ID: demo-session" \
  -d '{
    "model": "my_agent",
    "messages": [
      {
        "role": "user",
        "content": "妈妈昨晚起来四次，一直说有人偷钱，晚饭只吃了几口。我也快撑不住了。"
      }
    ],
    "stream": false
  }'
```

这条云端路径用于展示 Native Function Calling / Tool Calling。Android 隐私模式则用于展示 Edge AI。

### Android 构建

完整 Android 工程在主项目仓库中。本提交目录保留的是关键 Native 和 TypeScript 端侧模块。

```bash
cd frontend
npm install
npm run typecheck
cd android
NODE_ENV=production \
EXPO_PUBLIC_CAREMIND_API_URL=https://caremind-1039168666325.us-west1.run.app \
./gradlew :app:assembleRelease
```

## 隐私与安全边界

CareMind 处理的是失智症家庭照护数据，可能包含家庭冲突、照护者压力、用药观察和复诊资料。因此产品遵守以下边界：

- 敏感照护记录可在隐私模式下走端侧模型。
- 云端模式是可选路径，用于更完整的 Agent 工作流和长期摘要。
- 病历/检查资料进入复诊摘要前，需要家属确认。
- CareMind 不输出诊断、处方、用药调整或检查决策。
- 涉及急性风险或紧急情况时，应联系当地紧急服务或医生。

## 为什么选择 C 赛道

CareMind 的核心洞察不是“AI 可以总结文本”，而是：**最敏感的照护时刻往往发生在家里、深夜、照护者自己的手机上**。因此 Edge AI 是产品需求，而不是装饰性技术点。CareMind 希望让家属在不把每一段原始私密记录都交给云端的情况下，也能获得结构化照护理解和下一步支持。
