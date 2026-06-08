# MedComply Agent

MedComply Agent 是一个基于 Gemma 4 的医疗合规审查智能体，用于从 EHR 导出的 text-based PDF 病历中提取临床证据，并辅助 reviewer 完成 HEDIS 质量指标审查。

MedComply Agent is a Gemma 4 powered medical compliance review agent for extracting clinical evidence from text-based EHR PDF records and supporting human reviewers in HEDIS quality review workflows.

## 中文

### 项目简介

医疗合规审查中，reviewer 往往需要在病历 PDF 里手动查找血压、HbA1c、就诊类型、DOS、provider 等证据，再根据 HEDIS 指标判断 care gap 是否可以关闭。真实痛点是：证据分散、人工查找慢、规则判断需要稳定可审计、NSSD 回填容易重复录入。

MedComply Agent 用 Gemma 4 做 clinical evidence collection，通过 tool calling 从 text-based EHR PDF 中提取关键证据，并把 evidence、Agent Trace、PDF Locate 和 NSSD draft 呈现在 reviewer 工作台。最终 HEDIS 判断由后端 deterministic rule engine 完成，reviewer 保留最终确认权。

当前 demo 聚焦三个 HEDIS 指标：

- `CBP`: Controlling High Blood Pressure
- `BPD`: Blood Pressure Control for Patients with Diabetes
- `GSD`: Glycemic Status Assessment for Patients with Diabetes

核心功能：

- Gemma 4 tool-calling evidence collection
- Agent Memory 和可展开 Agent Trace
- BP / HbA1c / encounter / DOS / provider 等证据抽取
- PDF evidence locate 和高亮
- NSSD draft 自动回填
- 后端 HEDIS rule engine 确定性判断
- Human-in-the-loop reviewer confirmation

更详细的模型选型和架构设计见：

- `deliverables/technical-report.md`

### 数据来源与隐私保护

当前 demo 使用的测试病历全部为 AI 生成的模拟数据，不包含真实患者 PHI/PII。

真实生产环境中，MedComply Agent 应仅处理已授权的医疗数据，并使用与客户/医疗机构签署 BAA（Business Associate Agreement）的模型或云服务提供商。生产部署还应包含访问控制、审计日志、加密传输、最小权限、数据保留/删除策略，以及对 PHI 的合规处理流程。

### 输入边界

MedComply Agent 当前只接受 EHR 系统导出的 text-based PDF。OCR/scanned PDF 不属于当前 Agent review 范围。

### 项目目录

```text
.
├── backend/                 # FastAPI backend, Gemma agent, extraction service, HEDIS rules
│   ├── app/
│   │   ├── agent/           # Gemma tool schemas, agent loop, local tool execution
│   │   ├── api/             # HTTP routes
│   │   ├── db/              # Database session and seed logic
│   │   ├── models/          # SQLModel entities
│   │   ├── rules/           # Deterministic HEDIS rule engine
│   │   ├── schemas/         # API schemas
│   │   └── services/        # Extraction, provider, task status, confirmation services
│   ├── prompts/             # Legacy extraction prompts
│   ├── tests/               # Backend acceptance tests and mock records
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env.example
├── frontend/                # Next.js reviewer UI
│   ├── src/app/             # App routes and API proxy routes
│   ├── src/components/      # PDF viewer, review panels, UI components
│   ├── src/hooks/           # Review page state management
│   └── src/lib/             # API client, mappers, types, mock auth
├── samples/                 # Demo sample files
├── deliverables/            # Competition deliverables
├── docker-compose.yml       # PostgreSQL + backend + frontend
├── start.sh                 # One-command Docker startup
└── README.md
```

### 交付物

比赛交付物位于 `deliverables/`：

```text
deliverables/
├── technical-report.md                  # 技术报告：模型选型、架构设计、比赛要求对标
├── gemma-agent-run.log                  # Agent 运行日志：展示 Gemma tool calling / memory / trace
├── gemma-agent-run(BPD).png             # BPD 场景截图：血压指标审查示例
├── gemma-agent-run(GSD).png             # GSD 场景截图：HbA1c 指标审查示例
└── video-demo.mov                       # 演示视频：5 分钟内展示核心流程和真实痛点
```

### 快速启动

推荐使用 Docker Compose：

```bash
cp backend/.env.example backend/.env
```

编辑 `backend/.env` 并填写：

```env
LLM_API_KEY=<your-api-key>
```

默认 Gemma agent 配置：

```env
LLM_PROVIDER=openrouter
LLM_BASE_URL=https://openrouter.ai/api/v1
LLM_MODEL_NAME=google/gemma-4-26b-a4b-it
LLM_REVIEW_MODE=gemma_agent
```

启动：

```bash
./start.sh
```

访问：

- Frontend: http://localhost:3000
- Backend health check: http://localhost:8000/healthz

Demo 登录：

- Username: `admin`
- Password: `admin`

### 常用命令

停止服务：

```bash
docker compose down
```

清空本地 Docker volume：

```bash
docker compose down -v
```

Frontend 本地开发：

```bash
cd frontend
npm install
npm run dev
```

Backend 本地开发：

```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m alembic upgrade head
python -m uvicorn app.main:app --reload
```

验证：

```bash
cd frontend && npm run lint && npm run build
cd backend && python3 -m compileall app
```

## English

### Overview

MedComply Agent is a Gemma 4 based medical compliance review demo for HEDIS chart review. It currently supports:

- `CBP`: Controlling High Blood Pressure
- `BPD`: Blood Pressure Control for Patients with Diabetes
- `GSD`: Glycemic Status Assessment for Patients with Diabetes

The project addresses a practical review workflow: clinical evidence is scattered across PDF charts, manual lookup is slow, HEDIS rule decisions must be auditable, and NSSD fields are repetitive to fill. Gemma 4 performs tool-calling evidence collection, request-scoped Agent Memory, and Agent Trace generation. The backend deterministic rule engine makes the final HEDIS rule decision, and the reviewer confirms the result in the UI.

For model selection and architecture details, see:

- `deliverables/technical-report.md`

### Data and Privacy

All demo medical records are AI-generated synthetic test data. They do not contain real patient PHI/PII.

In production, MedComply Agent should process only authorized healthcare data and use AI/cloud providers covered by a BAA (Business Associate Agreement) with the customer or healthcare organization. A production deployment should also include access control, audit logging, encrypted transport, least-privilege permissions, retention/deletion policies, and PHI handling procedures.

### Input Boundary

MedComply Agent accepts text-based PDF files exported from EHR systems. OCR/scanned PDFs are outside the current Agent review scope.

### Repository Structure

```text
.
├── backend/                 # FastAPI backend, Gemma agent, extraction service, HEDIS rules
│   ├── app/
│   │   ├── agent/           # Gemma tool schemas, agent loop, local tool execution
│   │   ├── api/             # HTTP routes
│   │   ├── db/              # Database session and seed logic
│   │   ├── models/          # SQLModel entities
│   │   ├── rules/           # Deterministic HEDIS rule engine
│   │   ├── schemas/         # API schemas
│   │   └── services/        # Extraction, provider, task status, confirmation services
│   ├── prompts/             # Legacy extraction prompts
│   ├── tests/               # Backend acceptance tests and mock records
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env.example
├── frontend/                # Next.js reviewer UI
│   ├── src/app/             # App routes and API proxy routes
│   ├── src/components/      # PDF viewer, review panels, UI components
│   ├── src/hooks/           # Review page state management
│   └── src/lib/             # API client, mappers, types, mock auth
├── samples/                 # Demo sample files
├── deliverables/            # Competition deliverables
├── docker-compose.yml       # PostgreSQL + backend + frontend
├── start.sh                 # One-command Docker startup
└── README.md
```

### Deliverables

Competition deliverables are stored in `deliverables/`:

- `technical-report.md`: technical report covering model choice, architecture, and competition alignment
- `gemma-agent-run.log`: agent run log showing Gemma tool calling, memory, and trace
- `gemma-agent-run(BPD).png`: BPD scenario screenshot
- `gemma-agent-run(GSD).png`: GSD scenario screenshot
- `video-demo.mov`: demo video showing the core workflow and practical review pain points

### Quick Start

Docker Compose is the recommended setup path.

```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env`:

```env
LLM_API_KEY=<your-api-key>
```

Start the stack:

```bash
./start.sh
```

Open:

- Frontend: http://localhost:3000
- Backend health check: http://localhost:8000/healthz

Demo login:

- Username: `admin`
- Password: `admin`

### Common Commands

```bash
docker compose down
docker compose down -v
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Backend:

```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m alembic upgrade head
python -m uvicorn app.main:app --reload
```

Verification:

```bash
cd frontend && npm run lint && npm run build
cd backend && python3 -m compileall app
```
