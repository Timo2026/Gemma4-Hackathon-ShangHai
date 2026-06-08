# 律享宝 (LüXiangBao)

> 基于 Google Gemma 4 的全链路律师执业 AI Agent — Google Gemma 4 开发大赛参赛项目

---外链DEMO预览地址：https://lvxiangbao.zhaoyizu.com

## 📖 项目背景

中国律师在日常执业中面临大量重复性文书起草、法律工具查找、个人品牌运营等工作，耗费大量时间在格式化和检索上而非法律分析本身。**律享宝**应运而生——它是一款面向中国执业律师的全链路 AI 办案助手，借助 Google Gemma 4 大语言模型，覆盖律师从文书生成、工具导航到 IP 运营的核心工作流，让律师将精力聚焦于法律专业本身。

---

## ✨ 功能介绍

### 🖊️ 一、法律文书智能生成（21 类文书场景）

基于 Gemma 4 多步推理，端到端生成符合中国司法规范的 21 类法律文书：

| 场景 | 说明 |
|---|---|
| 类案检索报告 | 自动检索同类案件，生成结构化检索报告 |
| 案件汇报提纲 | 提炼案件要素，生成汇报提纲 |
| 审查报告（捕诉合一） | 全流程审查，一文书涵盖批捕与起诉 |
| 辩护词 / 公诉意见书 | 基于案情事实生成标准辩护/公诉文书 |
| 起诉状 / 答辩状 | 民事诉讼核心文书一键生成 |
| … | 共覆盖 21 类文书场景 |

**输入**：案件类型、当事人信息、案件事实、争议焦点、证据、案件阶段
**输出**：结构化 JSON + Markdown 格式的完整法律文书

### 📋 二、72 份法律文书模板库

提供 72 份标准法律文书模板，支持表单填写 + 智能渲染：

| 分类 | 数量 | 编号 |
|---|---|---|
| 民事诉讼通用文书 | 6 份 | MS-TY-001 ~ 006 |
| 民事诉讼案由专项文书 | 22 份 | MS-AY-001 ~ 022 |
| 法律援助业务文书 | 32 份 | FZ-001 ~ 032 |
| 律师辅助办案文书 | 12 份 | FZ-033 ~ 044 |

每份模板包含：
- 专用字段定义（字段名、标签、类型、是否必填、选项等）
- FreeMarker 模板渲染引擎（支持文本、日期、选择、数组、对象等字段类型）
- 填写表单 → 一键渲染 → 导出 HTML/纯文本

### 🔧 三、法律工具智能导航（12 大分类 · 27 个工具）

收录律师常用法律科技工具，分类导航 + AI 智能编排：

| 分类 | 代表工具 |
|---|---|
| 法律智能检索 | 秘塔 AI 搜索、微信 AI 搜索 |
| 合同智能审查 | 法天使 - 案牍 |
| 视听证据整理 | 通义听悟 |
| 法律文书写作 | AlphaGPT 法律 AI |
| 多场景法律翻译 | 智谱清言、DeepL、沉浸式翻译 |
| 司法公文撰写 | DeepSeek、新华妙笔、WPS AI |
| 案情文本可视化 | Mermaid |
| … | 共 12 大分类 27 个工具 |

**AI 编排**：用自然语言描述需求 → Gemma 4 推荐工具组合 → 生成使用教程 → 规划操作流程

### 🌟 四、律师 IP 智能运营

帮助律师打造个人品牌、合规获客：

| 功能 | 说明 |
|---|---|
| 个人简介包装 | 根据执业信息生成专业个人简介 |
| 合规案例描述 | 脱敏处理 + 合规描述成功案例 |
| 平台宣传素材 | 针对微信/抖音/小红书等平台生成定制素材 |
| 信任背书文案 | 生成专业资质、客户评价等信任内容 |
| 发布策略 | 基于律师定位生成内容发布时间表和策略 |

---

## 🏗️ 技术架构

```
┌─────────────────────────────────────────────────────┐
│                    前端 (Vue 3)                       │
│  Vite + Element Plus + Pinia + Vue Router + Axios   │
└──────────────────────┬──────────────────────────────┘
                       │ HTTP / REST API
┌──────────────────────▼──────────────────────────────┐
│                 后端 (Python FastAPI)                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐   │
│  │ API 路由  │→│ 业务服务  │→│ AI Agent (Gemma4) │   │
│  │ (5 模块)  │  │ (5 服务)  │  │  document_agent  │   │
│  └──────────┘  └──────────┘  │  tool_agent       │   │
│                               │  ip_agent         │   │
│  ┌──────────────────────┐    └──────────────────┘   │
│  │ 数据层 SQLAlchemy    │                            │
│  │ SQLite / MySQL       │    ┌──────────────────┐   │
│  └──────────────────────┘    │ Gemma4Client     │   │
│                               │ (OpenAI 兼容API) │   │
│                               └──────────────────┘   │
└─────────────────────────────────────────────────────┘
```

### 后端目录结构

```
backend/
├── app/
│   ├── main.py              # FastAPI 应用入口
│   ├── api/v1/              # API 路由层
│   │   ├── auth.py             用户认证（注册/登录/个人信息）
│   │   ├── documents.py        法律文书生成
│   │   ├── templates.py        模板库查询与渲染
│   │   ├── tools.py            法律工具导航与编排
│   │   └── ip.py               律师 IP 运营
│   ├── services/            # 业务逻辑层
│   │   ├── auth_service.py
│   │   ├── document_service.py
│   │   ├── template_service.py
│   │   ├── tool_service.py
│   │   └── ip_service.py
│   ├── agents/              # AI Agent 层（Gemma 4 交互）
│   │   ├── gemma4_client.py    Gemma 4 客户端封装
│   │   ├── document_agent.py   文书生成 Agent
│   │   ├── tool_agent.py       工具编排 Agent
│   │   └── ip_agent.py         IP 运营 Agent
│   ├── models/              # 数据模型
│   │   └── models.py           User / Document / Tool / IPMaterial / GenerationRecord
│   ├── data/                # 静态数据
│   │   ├── template_data.py    72 份模板定义 + 字段配置
│   │   └── navigation_data.py  12 分类 27 工具导航数据
│   └── core/                # 基础设施
│       ├── config.py           环境变量配置
│       ├── database.py         数据库连接
│       └── security.py         JWT 认证 + bcrypt 加密
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

### 前端目录结构

```
frontend/
├── src/
│   ├── views/
│   │   ├── home/               首页
│   │   ├── login/              登录/注册
│   │   ├── documents/          文书生成（列表/详情/生成）
│   │   ├── templates/          模板库（浏览/填写）
│   │   ├── tools/              工具导航（目录/编排）
│   │   ├── ip/                 IP 运营（仪表盘/案例/素材/背书）
│   │   ├── agent/              AI Agent 交互页
│   │   └── dashboard/          工作台
│   ├── stores/                 Pinia 状态管理
│   ├── router/                 路由配置
│   ├── utils/                  工具函数
│   └── styles/                 全局样式
├── package.json
└── vite.config.js
```

---

## 🚀 环境安装与启动

### 环境要求

| 依赖 | 版本要求 |
|---|---|
| Python | ≥ 3.10 |
| Node.js | ≥ 18.0 |
| npm | ≥ 9.0 |
| MySQL | ≥ 8.0（可选，默认使用 SQLite 零依赖启动） |
| Redis | ≥ 7.0（可选，本地开发不依赖） |

### 方式一：本地快速启动（推荐）

#### 1. 克隆项目

```bash
git clone https://github.com/your-username/lvxiangbao.git
cd lvxiangbao
```

#### 2. 启动后端

```bash
cd backend

# 创建 Python 虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate

# 安装 Python 依赖
pip install -r requirements.txt

# 配置环境变量（复制并编辑 .env 文件）
cp .env.example .env
# 编辑 .env 填入 Gemma 4 API Key（必填）和其他配置

# 启动后端服务
python -m app.main
# 或使用 uvicorn 直接启动
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

后端启动后访问：
- API 文档（Swagger）：http://localhost:8000/docs
- 健康检查：http://localhost:8000/health

#### 3. 启动前端

```bash
cd frontend

# 安装 Node.js 依赖
npm install

# 启动开发服务器
npm run dev
```

前端启动后访问：http://localhost:5173

#### 4. 配置 Gemma 4 API Key

在 `backend/.env` 中配置 Google Gemma 4 的 API Key（支持 GMI Cloud / Google AI Studio 等兼容 OpenAI 接口的服务）：

```env
# 必填：Gemma 4 API Key
GEMMA4_API_KEY=your_api_key_here

# 可选：API Base URL（默认使用 GMI Cloud）
GEMMA4_BASE_URL=https://api.gmi.cloud/v1

# 可选：模型名称（默认 gemma-4-14b）
GEMMA4_MODEL=gemma-4-14b
```

> 💡 无 API Key 也可启动，系统将使用内置模拟模式（Mock Mode）运行，所有 AI 功能返回模拟结果。

### 方式二：Docker Compose 一键部署

```bash
cd backend

# 配置环境变量
cp .env.example .env
# 编辑 .env 填入 GEMMA4_API_KEY 等配置

# 一键启动（MySQL + Redis + 后端）
docker-compose up -d

# 查看日志
docker-compose logs -f backend
```

Docker 模式会自动启动：
- MySQL 8.0（端口 3306）
- Redis 7（端口 6379）
- 后端服务（端口 8000）

前端仍需单独启动（或使用 `npm run build` 后将 dist 目录部署至 Nginx）。

---

## 🔑 环境变量说明

| 变量名 | 默认值 | 说明 |
|---|---|---|
| `GEMMA4_API_KEY` | （空） | **必填** Google Gemma 4 API Key |
| `GEMMA4_BASE_URL` | `https://api.gmi.cloud/v1` | Gemma 4 API 地址 |
| `GEMMA4_MODEL` | `gemma-4-14b` | 使用的模型名称 |
| `DATABASE_URL` | `sqlite:///./lvxiangbao.db` | 数据库连接串（SQLite 或 MySQL） |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis 连接串（可选） |
| `SECRET_KEY` | `lvxiangbao-secret-key-...` | JWT 签名密钥（生产环境务必修改） |
| `DEBUG` | `true` | 调试模式 |

---

## 📡 API 接口一览

| 模块 | 方法 | 路径 | 说明 |
|---|---|---|---|
| 认证 | POST | `/api/v1/auth/register` | 用户注册 |
| 认证 | POST | `/api/v1/auth/login` | 用户登录 |
| 认证 | GET | `/api/v1/auth/profile` | 获取个人信息 |
| 认证 | PUT | `/api/v1/auth/profile` | 更新个人信息 |
| 文书 | GET | `/api/v1/documents/scenarios` | 获取 21 类文书场景 |
| 文书 | POST | `/api/v1/documents/generate` | AI 生成法律文书 |
| 文书 | GET | `/api/v1/documents` | 文书列表 |
| 文书 | GET | `/api/v1/documents/{id}` | 文书详情 |
| 模板 | GET | `/api/v1/templates/categories` | 模板分类树 |
| 模板 | GET | `/api/v1/templates` | 模板列表（支持分类/关键词筛选） |
| 模板 | GET | `/api/v1/templates/{id}` | 模板详情（含字段定义） |
| 模板 | POST | `/api/v1/templates/render` | 填写表单渲染文书 |
| 工具 | GET | `/api/v1/tools/catalog` | 工具分类目录 |
| 工具 | GET | `/api/v1/tools/navigation` | 首页导航数据 |
| 工具 | POST | `/api/v1/tools/orchestrate` | AI 工具编排推荐 |
| 工具 | POST | `/api/v1/tools/ai-tutorial` | AI 定制工具教程 |
| IP | GET | `/api/v1/ip/platforms` | 支持平台列表 |
| IP | POST | `/api/v1/ip/profile` | 生成个人简介包装 |
| IP | POST | `/api/v1/ip/case` | 生成合规案例描述 |
| IP | POST | `/api/v1/ip/material` | 生成平台宣传素材 |
| IP | POST | `/api/v1/ip/trust-content` | 生成信任背书文案 |
| IP | POST | `/api/v1/ip/strategy` | 生成发布策略 |

完整 API 文档启动后访问：http://localhost:8000/docs

---

## 🧩 核心技术栈

| 层级 | 技术 | 版本 |
|---|---|---|
| AI 模型 | Google Gemma 4 | gemma-4-14b |
| 后端框架 | FastAPI | ≥ 0.104 |
| ASGI 服务器 | Uvicorn | ≥ 0.24 |
| ORM | SQLAlchemy | ≥ 2.0 |
| 数据校验 | Pydantic | ≥ 2.5 |
| AI SDK | OpenAI Python SDK | ≥ 1.55 |
| 认证 | python-jose + bcrypt | JWT + bcrypt |
| 数据库 | SQLite（开发）/ MySQL 8.0（生产） | — |
| 缓存 | Redis 7（可选） | — |
| 前端框架 | Vue 3 | 3.4 |
| UI 组件库 | Element Plus | 2.6 |
| 状态管理 | Pinia | 2.1 |
| 构建工具 | Vite | 5.2 |
| HTTP 客户端 | Axios | 1.6 |
| 容器化 | Docker + Docker Compose | — |

---

## 📄 许可证

本项目为 Google Gemma 4 开发大赛参赛作品。

