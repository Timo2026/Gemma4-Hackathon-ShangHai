# Lonely FM（在吗？）

赛道：D - Social Good  
队伍：Stay Spark 星驻  
成员：Johnny Wang、Tim Tsui  
线上体验：https://lonely-fm.vercel.app/  
完整项目仓库：https://github.com/JohnnyWang8802/lonely-fm  
演示视频：https://youtu.be/RzLeD7CA_Sw  
技术报告：`docs/TECHNICAL_REPORT.md`，PDF 版见 `docs/Lonely-FM-Gemma4-Hackathon-Submission.pdf`

Lonely FM 是一个基于 Gemma 4 的纯语音陪伴工具，面向深夜、独居、疲惫或暂时不知道该向谁开口的人。它不是替代朋友、家人或专业帮助，而是在用户最孤独、最说不出口的时刻，先提供一个愿意认真听完的声音。

## 核心体验

- 纯语音交互：用户进入频道、选择林屿或阿婉后，用说话完成对话，不需要打开聊天窗口。
- 连接式启动：参考真实通话体验，点击角色后先显示“正在连接”，用于预热本地 Gemma 4 和语音链路；接通后角色主动打招呼。
- 情绪化回应：后端根据转写文本、语速/停顿等信号生成情绪标签，Gemma 4 在回答时会参考用户当下状态。
- 长期记忆：登录用户可以跨设备保留愿意留下的记忆；访客模式不持久化记忆，离开对话页即结束本次体验。
- 本地优先：默认优先连接用户电脑上的 Ollama / Gemma 4，本地模型不可用时才提示使用云端 Gemma 4 API key。

## Gemma 4 使用方式

本项目将 Gemma 4 作为对话和陪伴策略的核心模型，重点使用端侧部署能力：

- 默认模型服务：Ollama 本地 Gemma 4。
- 兼容标签：`gemma4:*`，例如 `gemma4:12b-mlx`、`gemma4:e4b`、`gemma4:21b`。
- 云端备选：支持用户输入自己的 Google AI / Gemma 4 API key，适合手机、平板或没有本地模型的测试场景。
- 预热机制：在“正在连接”阶段调用 `prewarm()`，让本地模型加载和 prompt KV cache 尽量提前完成。
- 流式回复：后端以 WebSocket 推送 token、文本片段和 TTS 音频，前端边收到边播放，降低长空白。
- 结构化上下文：Gemma 4 的 prompt 会注入角色身份、最近对话、长期记忆、情绪信号和安全边界。

核心代码位置：

- `backend/services/gemma.py`：本地 / 云端 Gemma 4 选择、状态检测、预热和流式生成。
- `backend/routers/ws.py`：实时语音 WebSocket 管线，整合 STT、情绪识别、Gemma 4 和 TTS。
- `backend/prompt/persona.py`：林屿 / 阿婉角色提示词、自然口语规则、记忆和安全边界。
- `frontend/src/App.tsx`：首页、登录、Gemma 连接、声线选择、对话页和信息页。
- `supabase/migrations/20260604_create_memories.sql`：登录用户长期记忆表和 RLS 策略。

## 技术架构

```text
Browser
  ├─ Voice UI / VAD / Live caption
  ├─ Supabase Auth
  └─ WebSocket audio stream
        ↓
FastAPI Backend
  ├─ STT: OpenAI Whisper or browser transcript fallback
  ├─ Emotion: Hume API or local prosody fallback
  ├─ Memory: Supabase user-scoped memory
  ├─ Gemma 4: local Ollama first, cloud API optional
  └─ TTS: MiniMax / Google TTS
        ↓
Streaming text + streaming/queued audio
        ↓
Voice companion interface
```

## 本地运行

### 1. 准备 Gemma 4

安装并启动 Ollama，然后拉取任意 Gemma 4 标签：

```bash
ollama pull gemma4:12b-mlx
```

如果使用线上 Vercel 前端访问本地 Ollama，需要允许浏览器来源：

```bash
launchctl setenv OLLAMA_ORIGINS "https://lonely-fm.vercel.app,http://localhost:5173,http://127.0.0.1:5173"
```

重启 Ollama 后，再在页面中点击“重新检测本地 Gemma”。

### 2. 后端

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp ../.env.example ../.env
uvicorn main:app --reload --port 8001
```

### 3. 前端

```bash
cd frontend
pnpm install
pnpm dev
```

打开 `http://localhost:5173`。

## 环境变量

复制 `.env.example` 为 `.env` 后按需填写：

- `GEMMA_PROVIDER=local`：默认使用本地 Gemma 4。
- `LOCAL_GEMMA_BASE_URL=http://127.0.0.1:11434`：Ollama 地址。
- `GOOGLE_AI_API_KEY`：云端 Gemma 4 API key，可选。
- `MINIMAX_API_KEY`：MiniMax TTS，可选；不填会使用降级语音链路。
- `OPENAI_API_KEY`：Whisper STT，可选。
- `SUPABASE_URL` / `SUPABASE_ANON_KEY`：邮箱登录和长期记忆。

## 数据合规与隐私保护

Lonely FM 属于 Social Good 场景，隐私是产品设计的一部分：

- 访客模式不保存长期记忆，离开对话页即结束本次会话。
- 登录用户的长期记忆按 Supabase Auth 用户隔离，用户可删除记忆。
- 默认优先本地 Gemma 4，敏感对话可以尽量留在用户自己的设备上。
- 云端 Gemma 4 API 是用户主动选择的备选路径，适合移动端或临时测试。
- 产品明确不替代医疗、心理咨询、法律等专业帮助；遇到自伤或危机表达时会触发安全回应。

## 目录说明

```text
backend/       FastAPI 实时语音后端
frontend/      React + Vite 前端
supabase/      长期记忆数据库迁移
docs/          技术报告（Markdown + PDF）
requirements.txt
```

## 当前限制

- 线上 Vercel 只承载前端；如果使用本地 Gemma 4，用户电脑需要已安装并启动 Ollama。
- MiniMax TTS、Whisper STT、Supabase 邮件服务需要配置各自 API key。
- 本地模型冷启动时首轮可能偏慢，产品通过“正在连接”画面和模型预热缓冲这段等待。
