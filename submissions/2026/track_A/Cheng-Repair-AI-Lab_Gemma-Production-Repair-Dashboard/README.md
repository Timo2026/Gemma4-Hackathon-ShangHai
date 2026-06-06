# Gemma 产线维修智能数据看板

> **参赛组名**：Cheng Repair AI Lab　｜　**正式项目名称**：Gemma 产线维修智能数据看板
> 仓库历史名称 / 在线地址 slug 仍为 `gemma4-repair-dashboard`（仅作仓库历史名称，不作正式项目名）

面向工厂产线维修场景的 **AI Agent 维修数据看板**。以 **Gemma 4（`gemma-4-26b-a4b-it`）** 为核心，演示维修现场数据可视化、修复率 / WIP 数字孪生监控、领退料异常预警与协同推送配置预留，并通过后端自实现的 **模型驱动函数调用循环** 让 Gemma 4 自主取数、多步推理、产出维修管理汇报。

---

## 1. 项目名称

- **正式项目名称**：Gemma 产线维修智能数据看板
- **参赛组名**：Cheng Repair AI Lab
- **仓库历史名称**：`gemma4-repair-dashboard`（在线演示 / 仓库地址 slug，仅作历史名称，不作正式项目名）

---

## 2. 项目简介

工厂维修课每天面对大量待修工单、WIP 积压、不良缺陷与领退料异常，依赖人工逐表统计、口径不一、响应滞后。本项目把维修现场的多源数据汇聚成三块联动看板，并接入 Gemma 4 作为分析智能体，自动完成「取数 → 推理 → 汇报」的闭环，辅助现场管理者快速定位积压、超期与异常，驱动闭环改善。

项目包含三块核心看板：

- **产线维修综合看板**：出勤、维修趋势、个人产出等综合分析视图，由 Gemma 分析层自动生成 WIP / 修复率管理汇报。
- **维修修复率看板**：面向 WIP 与不良分析的修复率监控，聚焦待修积压、超期工单预警、不良 TOP 缺陷、原因分布与各组修复率排行。
- **领退料异常预警看板**：维修领料 / 退料闭环与超时异常预警，确保备件闭环管理。

项目提供两种运行形态：**纯前端离线 Demo（零配置，默认）** 与 **真实 Gemma 4 后端（可选，自带 Key 即可复现）**。默认全部使用脱敏演示数据，不含任何真实生产数据。

---

## 3. 在线演示链接

GitHub Pages 在线演示：

<https://cheng137930948-l.github.io/gemma4-repair-dashboard/>

> 在线 Demo 为纯前端静态页面，AI 分析为离线演示效果；要复现真实 Gemma 4 函数调用循环，请按「运行方式 → 真实 Gemma 4 后端」在本地启动。

---

## 4. 演示视频链接

5 分钟演示视频：

<https://github.com/cheng137930948-l/gemma4-repair-dashboard/releases/download/v1.0-demo/default.mp4>

---

## 5. 项目仓库链接

GitHub 仓库：

<https://github.com/cheng137930948-l/gemma4-repair-dashboard>

---

## 6. 运行方式

### 方式一 · 纯前端离线（零配置，最快）

1. 下载或克隆本仓库。
2. 双击根目录下的 `index.html` 进入首页（推荐用静态服务器打开，Excel 导入 / 导出依赖相对路径）：
   ```bash
   python -m http.server 8123
   # 浏览器访问 http://127.0.0.1:8123/index.html
   ```
3. 首页点击三个核心入口，分别进入综合看板、领退料看板、修复率看板。此模式 AI 为离线模拟。

### 方式二 · 真实 Gemma 4 后端（自带 Key 即可复现）

同时拉起【后端 `:8001` + 前端 `:8123`】，首页「AI 智能分析中心」点「开始分析」即走真实 Gemma 4 原生函数调用循环。

**环境要求**：Python 3.10+（仅真实后端需要；纯前端方式一无需任何环境）。

**手动安装并启动**（环境步骤，与脚本等价，便于排查）：

```bash
# 1) 安装后端依赖（在项目根目录执行）
pip install -r requirements.txt

# 2) 配置 Key：复制占位模板并填入自己的 GOOGLE_API_KEY
cp backend/.env.example backend/.env
# 编辑 backend/.env，填入 https://aistudio.google.com/apikey 申请的 GOOGLE_API_KEY

# 3) 启动后端（:8001）
cd backend && python report_server.py

# 4) 另开一个终端，在项目根目录启动前端（:8123）
python -m http.server 8123
# 浏览器访问 http://127.0.0.1:8123/index.html
```

或用下面的一键脚本 / Docker（自动完成上述步骤）：

**本地脚本**（自动建 venv、装依赖、起前后端）：

```bash
./start.sh
# 首次会生成 backend/.env —— 填入 GOOGLE_API_KEY（https://aistudio.google.com/apikey）后重跑
# 启动后打开 http://127.0.0.1:8123/index.html
```

**Docker**（一条命令）：

```bash
GOOGLE_API_KEY=你的Key docker compose up
# 或在本目录建 .env 写 GOOGLE_API_KEY=...，再 docker compose up
# 启动后打开 http://127.0.0.1:8123/index.html
```

> **时延提示**：`gemma-4-26b-a4b-it` 单次推理约 10–20s，一次多轮函数调用端到端通常 40–95s（模型多轮取数推理，非 bug）。若需现场零等待，可先 `cd backend && python warm_cache.py` 预热，再在 `backend/.env` 设 `REPLAY_ONLY=1` 重启后端，即可秒回真实跑批缓存。详见 `backend/README.md`。

> **密钥安全**：真实 `GOOGLE_API_KEY` 仅写入本地 `backend/.env`（已被 `.gitignore` 排除，不入仓库），仓库仅提供 `backend/.env.example` 占位模板。

---

## 7. 技术栈

**前端**

- 原生 HTML / CSS / JavaScript（三块看板为独立页面，首页统一入口）
- ECharts 数据可视化（修复率排行 / 进出板 / 不良 TOP5 / 原因分布等图表）
- SheetJS（`libs/xlsx.full.min.js`，本地离线依赖，支持 Excel 导入 / 导出）
- `gemma_config.js` / `gemma_adapter.js`：前端模型配置与离线分析适配层（planner / 工具调用 / trace）

**后端（可选）**

- Python + Flask 精简服务（`backend/report_server.py`，路由 + 单轮兜底 + 录制回放缓存）
- `google-genai` SDK 真实调用 **Gemma 4（`gemma-4-26b-a4b-it`）**
- 自实现的 **模型驱动函数调用循环**（`backend/agent.py` + `backend/tools.py`）
- Markdown Skill 规则注入（`backend/skills/repair-report/SKILL.md`）

**部署**

- GitHub Pages 静态托管（含 `.nojekyll`，支持中文文件名路径）
- Docker / docker-compose 一键启动

---

## 8. 项目亮点

- **在 Gemma 4 上自实现函数调用循环**：Gemma 4 是开放权重模型，在 Gemini API 上只支持 `generateContent`，不提供 `tools=` 参数。本项目不退回「把数据一次性塞进 prompt」的提示工程，而是按 Gemma 4 函数调用约定，在 `agent.py` 中自行实现由模型驱动的多轮循环——把工具清单注入 prompt，模型自主输出 ```` ```tool_code ````，后端解析、在 `tools.py` 真实执行、再以 ```` ```tool_output ```` 回灌，多轮推理直至产出最终汇报。这是真正的「模型驱动多步函数调用」，且完全符合 Gemma 4 接口约束。

- **每一步可追溯**：每次工具调用都记录在 `trace`，并落盘为 `backend/output/agent_run_*.log` 运行日志，分析过程可复现、可审计。

- **三看板口径一致、数字孪生联动**：综合看板的 AI 汇报与修复率看板共用同一口径（修复率约 81%），WIP / 修复率 / 不良 / 领退料指标互相印证。

- **演示稳定性工程**：针对模型时延做了单次硬超时、5xx/504 退避重试、循环总时长预算与「录制回放」模式（展示的仍是真实 Gemma 4 跑批结果，只是改为零等待回放），保证现场演示不中断；函数调用不可用时自动回退单轮生成。

- **零配置可演示 + 自带 Key 可复现**：默认纯前端离线即可完整走查三看板；评审用自己的 Key 启动后端即可复现真实 Gemma 4 推理，两条路径互不阻塞。

- **安全与脱敏到位**：全仓库使用脱敏演示数据，不含真实 Webhook、账号密码、客户数据或内部接口地址；真实 API Key 仅存本地 `.env` 占位隔离。

---

## 9. 交付物说明

| 交付物 | 位置 / 链接 |
|---|---|
| 项目仓库 | <https://github.com/cheng137930948-l/gemma4-repair-dashboard> |
| 在线演示 | <https://cheng137930948-l.github.io/gemma4-repair-dashboard/> |
| 演示视频（5 分钟） | <https://github.com/cheng137930948-l/gemma4-repair-dashboard/releases/download/v1.0-demo/default.mp4> |
| 技术报告 | `技术报告.md` |
| 演示视频脚本 | `演示视频脚本.md` |
| 真实落地佐证 | `docs/真实落地佐证.md` + `docs/evidence/`（脱敏截图） |

**目录结构**

```text
gemma4-repair-dashboard/
├─ backend/                        # 真实 Gemma 4 后端（可选）
│  ├─ report_server.py             # Flask 服务：路由 + 单轮兜底 + 录制回放缓存
│  ├─ agent.py                     # 函数调用循环（解析 / 执行 / 回灌 / trace / 重试 / 时长预算）
│  ├─ tools.py                     # 后端工具注册表（get_wip 等，返回 {summary, data}）
│  ├─ demo_data.py                 # 三看板脱敏演示数据（后端兜底，口径与前端一致）
│  ├─ warm_cache.py                # 录制预热：三看板各真跑一次并缓存，供回放秒回
│  ├─ requirements.txt             # 后端依赖
│  ├─ .env.example                 # API Key 占位 + 模型 / 超时 / 回放等配置说明
│  ├─ README.md                    # 后端启动说明（含时延与录制回放）
│  └─ skills/repair-report/SKILL.md  # 注入为分析 Prompt 的汇报技能
├─ data/demo/                      # 脱敏演示数据（integrated / material）
├─ replay/                         # 真实 Gemma 4 跑批回放缓存（用于零等待演示）
├─ docs/                           # 技术佐证与脱敏截图
├─ icons/                          # 图标资源
├─ libs/                           # 本地离线依赖（xlsx.full.min.js）
├─ requirements.txt                # 后端依赖（根目录一键装：pip install -r requirements.txt）
├─ index.html                      # Demo 首页（三看板入口 + AI 智能分析中心）
├─ gemma_config.js                 # Gemma 模型配置（gemma-4-26b-a4b-it / demoMode）
├─ gemma_adapter.js                # 前端分析适配层（planner / 工具 / trace）
├─ material_dashboard.js           # 领退料看板脚本
├─ 产线维修综合看板_v3.html          # 产线维修综合看板
├─ 产线维修课领退料看板.html          # 产线维修领退料看板
├─ 修复率看板.html                   # 维修修复率看板
├─ 技术报告.md                       # 技术报告
└─ 演示视频脚本.md                    # 演示视频脚本
```

**脱敏与安全声明**

- 全部为脱敏演示数据，不代表真实生产数据，不含真实 Webhook、Cookie、账号密码、客户敏感数据或内部接口地址。
- 真实 API Key 仅存于本地 `backend/.env`（已被 `.gitignore` 排除），仓库仅提供 `.env.example` 占位。
- 请勿在公开仓库中提交真实 API Key、Token、Webhook、Cookie、人员隐私或生产接口地址。
