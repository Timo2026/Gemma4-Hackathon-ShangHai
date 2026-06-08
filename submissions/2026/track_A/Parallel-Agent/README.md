# Parallel Agent

**Team:** VirtuOasis  
**Track:** A - AI Agent  
**Core model:** Gemma 4

Hackathon materials:

- Technical report: `TECHNICAL_REPORT.md`
- Native Function Calling tool: `simulate_reality_turn`
- Tool-call evidence: Web session page section `Gemma Native Function Calling`
- 运行日志：见下方 [黑客松评审材料](#黑客松评审材料agent-memory-与-tool-calling-证据)
- 项目介绍视频：见下方 [项目介绍](#项目介绍视频)

---

## 项目介绍

<p align="center">
  <video src="./media/presentation-video-web.mp4" controls width="420">
    你的浏览器/渲染器不支持内嵌视频，请点击下方链接观看。
  </video>
</p>

> 视频文件：[`media/presentation-video-web.mp4`](./media/presentation-video-web.mp4)

---

`Parallel Agent` 是一个面向复杂人生/职业决策的多路径决策引擎。

Parallel Agent = 多宇宙决策模拟引擎（Multi-Universe Decision Engine）

它帮助用户：
- 探索多种可能的未来
- 了解长期影响
- 在行动前做出更明智的决定

```
parallel-agent = Environment × Agent
               ↕               ↕
           环境模拟          行为主体
          （动态背景）      （决策者 + 社会）
```


用户输入一个场景，系统会生成 3-4 条平行未来分支；用户选择其中一条后，系统会把这条路径坍缩为当前现实，并继续生成下一轮分支，最多迭代 5 轮，最后输出完整的决策旅程总结。

它更像一个可交互的多宇宙决策模拟器

---

`Parallel Agent` 想解决的问题是：

> 当人面对重要选择时，往往不是缺少一个答案，而是缺少对“不同未来会怎样展开”的可感知理解。

所以它的核心体验不是“告诉你怎么选”，而是：

1. 为一个困境生成多个有差异的未来分支
2. 让你观察每条分支的后果、风险和社会反应
3. 让你选择其中一条继续推进
4. 把你之前的选择记忆带入下一轮
5. 最终生成一段完整的决策路径总结

---
## 黑客松评审材料：Agent Memory 与 Tool Calling 证据

> 评审要求：代码中需清晰展示 Agent 的 **Memory** 和 **Tool Calling** 逻辑，并提供运行日志截图。
>
> 下面把每张截图对应到具体的 Memory / Tool Calling 机制，并给出代码位置。

### 1. Tool Calling：运行日志（runtime log）

每次推进一轮，Web 层会调用 `POST /api/session/start` 与 `POST /api/session/choose`，底层由 Gemma 4 原生调用工具 `simulate_reality_turn` 生成完整 turn simulation。下图是本地 Ollama（`gemma4:latest`）运行时的 dev server 日志，可以看到逐轮 session 调用与工具执行耗时。

<p align="center">
  <img src="./media/Screenshot%202026-06-08%20at%2018.54.23.png" alt="运行日志：Gemma 4 原生工具调用与逐轮 session 请求" width="520">
</p>

- **Tool Calling 代码位置**：原生工具 `simulate_reality_turn`，结果状态 `validated`
- **CLI 工具调用证据**：`npm run eval:gemma:smoke` 会输出 `toolCalls=simulate_reality_turn:validated`
- **持久化**：待选轮次的工具调用保存在 `pendingTurn.toolCalls`，坍缩后保存在 `session.toolCalls`

### 2. Memory：决策记忆四视图

下面四张截图分别展示 Agent 记忆链的不同切面：会话状态总览、个人↔社会影响链、多轮分支坍缩、消融实验与最终总结。

<table>
  <tr>
    <td width="50%" valign="top">
      <img src="./media/Screenshot%202026-06-08%20at%2018.56.16.png" alt="会话总览：脑图式路径回放与个人/社会状态" width="100%"><br>
      <b>会话状态总览</b><br>
      <code>canonicalPath</code> 已坍缩路径、<code>shadowTimelines</code> 未选路径、<code>simulationState</code> 个人/环境指标
    </td>
    <td width="50%" valign="top">
      <img src="./media/Screenshot%202026-06-08%20at%2018.56.26.png" alt="个人与社会双向影响链及社会角色状态" width="100%"><br>
      <b>个人 ↔ 社会影响链</b><br>
      <code>quantumTrace</code> 残留记忆、<code>InfluenceEvent</code> 双向影响、stakeholder trust / resistance / influence
    </td>
  </tr>
  <tr>
    <td width="50%" valign="top">
      <img src="./media/Screenshot%202026-06-08%20at%2018.57.04.png" alt="每轮候选分支与坍缩结果" width="100%"><br>
      <b>多轮分支生成与坍缩</b><br>
      每轮 <code>branches</code> + 坍缩结果，逐轮写入 <code>canonicalPath</code>
    </td>
    <td width="50%" valign="top">
      <img src="./media/Screenshot%202026-06-08%20at%2018.57.11.png" alt="消融实验对比与最终角色总结" width="100%"><br>
      <b>消融实验与最终总结</b><br>
      <code>session.toolCalls</code> 重放、ablation report（事件数 / 差异距离 / delta）、final summary
    </td>
  </tr>
</table>

---

## 核心功能

当前项目已经具备这些能力：

- 输入一个 dilemma，生成 3-4 个平行决策分支
- 每个分支包含：
  - 标题
  - 摘要
  - 后果
  - 风险画像
  - 世界变化
  - 社会/利益相关者反应
- 用户选择一个分支后，系统推进到下一轮
- 系统会保留：
  - `canonicalPath` 已选路径
  - `shadowTimelines` 未选路径
  - `quantumTrace` 决策残留记忆
  - `userPersona` 用户状态变化
  - `simulationState` 个人、社会角色和环境指标
- 支持最终 summary 生成
- 支持本地 session 持久化
- 支持 headless harness 和 Web/API 两种使用方式
- 支持 grounded preset scenario（当前已落地 `ai_future_of_work`）
- 支持在 grounded preset 下覆盖最小 `User Context Pack`
- 支持最小 grounding evidence / grounding log，帮助回看 scenario facts 如何影响生成
- 支持 `InfluenceEvent` 因果事件，记录 individual / society / environment 之间的双向影响
- 支持 Gemma 4 Native Function Calling：Gemma 原生调用 `simulate_reality_turn` 工具返回完整 turn simulation
- 支持记录 `tool_calls`：待选择轮次保存在 `pendingTurn.toolCalls`，坍缩后保存在 `session.toolCalls`
- 支持确定性 influence reducer：Gemma 生成影响事件，Parallel Agent 负责把事件更新为可比较的模拟状态
- 支持 ablation comparison：同一条已坍缩路径可以重放为 Full / No Individual Influence / No Society Influence / Isolated Baseline 四组实验
- Gemma 4 默认使用 unified turn simulation：每轮一次模型调用生成 branches、world deltas、communities 和 influence events

---


## 架构：Environment × Agent

parallel-agent 的整个系统可以被干净地切成两个维度：

```
┌─────────────────────────────────────────────────────────────┐
│                        Parallel Agent                               │
│                                                             │
│    ENVIRONMENT（环境模拟）        AGENT（行为主体）          │
│    ─────────────────────         ──────────────────         │
│    定义"什么是可能的"            定义"谁在行动"             │
│                                                             │
│    v1: 训练数据                    Multi-Agent               │
│         + quantumTrace            （社会/社区）              │
│                                   → LLMAction               │
│    v2: 真实 API 数据              → 自主演化                 │
│         + 知识图谱                                          │
│                                   Single Agent              │
│    v3: 专业仿真模型               （用户代理）               │
│         SEIR / Monte Carlo        → ManualAction            │
│                                   → 观测触发坍缩             │
└─────────────────────────────────────────────────────────────┘
```

### 三条交互规则

1. **Environment 约束 Agent，不控制 Agent** — 世界设定边界，Agent 在边界内自由决策
2. **Multi-Agent 行为反馈到 Environment** — 社区反应改变下一轮世界状态
3. **Single Agent 是唯一 ManualAction** — 只有用户的观测能触发波函数坍缩

---

## 快速开始

### 1. 安装依赖

```bash
npm install
```

### 2. 配置模型环境变量

在项目根目录创建或编辑 `.env.local`。

Harness 脚本现在会自动读取 `.env.local`，不需要再手动执行 `source .env.local`。

黑客松展示核心模型是本地 `Gemma 4` / Ollama。

本地 `Gemma 4` / Ollama：

```env
PARALLEL_AGENT_MODEL_PROVIDER=gemma
GEMMA_RUNTIME=ollama
OLLAMA_BASE_URL=http://localhost:11434
GEMMA_MODEL=gemma4:latest
```

如果使用 Hugging Face Router：

```env
PARALLEL_AGENT_MODEL_PROVIDER=gemma
GEMMA_RUNTIME=huggingface
HF_TOKEN=your_huggingface_token_here
GEMMA_MODEL=google/gemma-4-26B-A4B-it:novita
```

可选配置：

```env
GEMMA_MAX_TOKENS=6000
GEMMA_TEMPERATURE=0.7
PARALLEL_AGENT_TURN_SIMULATOR=unified
PARALLEL_AGENT_LANGUAGE=zh-CN
```

`PARALLEL_AGENT_LANGUAGE=zh-CN` 会要求 Gemma 将所有用户可见的自然语言字段生成为简体中文，同时保持 JSON key、id 和 enum 为英文。设置为 `en` 可切回英文。

`PARALLEL_AGENT_TURN_SIMULATOR=unified` 是 Gemma 4 默认展示路径。一轮 Gemma 4 调用会返回完整 turn simulation。需要回退旧两段式 branch + society pipeline 时，可以设置：

```env
PARALLEL_AGENT_TURN_SIMULATOR=legacy
```

---

## 如何使用

## 方式 1：本地交互式 Harness

启动交互式命令行体验：

```bash
npm run dev
```

只要 `.env.local` 已填写好可用的 provider 配置，上面的命令会自动加载它。

Gemma 4 自动 demo：

```bash
npm run dev:gemma:auto
```

如果你只想快速看 mock 结果：

```bash
npm run dev:mock
```

自动跑 demo：

```bash
npm run dev:mock:auto
```

查看已保存 session：

```bash
npm run dev:list
```

恢复某个 session：

```bash
npm run dev:resume -- <sessionId>
```

如果 `.env.local` 中没有可用 API key，harness 会提示你改用 `npm run dev:mock`。

当前 grounded demo 也支持直接从 preset scenario 启动：

- 选择 `ai_future_of_work`
- 按需覆盖：
  - `userGoal`
  - `currentPosition`
  - `riskPreference`
  - `timeHorizon`
  - `personalConstraints`
  - `keyStakeholders`

这样同一个 preset world 可以测试不同 user case 是否产生不同 branch / society / summary。

---

## 方式 2：最小 Web 界面

启动 Web：

```bash
npm run web:dev
```

使用 Gemma 4 启动 Web：

```bash
npm run web:gemma
```

使用 Gemma 4 跑结构化 smoke evaluation：

```bash
npm run gemma:smoke
npm run eval:gemma:smoke
```

`npm run eval:gemma:smoke` 会在终端输出 tool call 记录，例如：

```text
toolCalls=simulate_reality_turn:validated
```

默认使用本地 Ollama 后端：

```env
PARALLEL_AGENT_MODEL_PROVIDER=gemma
GEMMA_RUNTIME=ollama
OLLAMA_BASE_URL=http://localhost:11434
GEMMA_MODEL=gemma4:latest
```
打开浏览器访问：

- `http://localhost:3000`

Web 默认使用中文界面和中文生成。起始页可以通过“输出语言”切换中文或英文。

你可以：

1. 输入一个 dilemma
2. 选择 theme 和 turns
3. 选择自由输入或 `ai_future_of_work` preset
4. 在 `ai_future_of_work` 下覆盖最小 `User Context Pack`
5. 启动 session
6. 查看分支
7. 选择某条分支继续推进
8. 查看最终 summary、grounding evidence 和 grounding log

Gemma 4 demo 还会在 session 页面展示 `Working pipeline`：

- Human movement：用户如何在 decision space 中移动
- Environment dynamics：每次 collapse 后世界压力、约束、机会和 stakeholder reaction 如何变化
- Gemma / LLM steps：生成式 agent 层做了什么
- Parallel Agent core steps：本地确定性状态机做了什么

session 页面也会展示 `Gemma Native Function Calling`：

- 原生工具名：`simulate_reality_turn`
- provider：`Gemma 4 (gemma4:latest, ollama)`
- status：`validated`
- result summary：turn、branch、community 和 influence event 数量

session 页面也会展示 `Simulation state`：

- individual：confidence、reputation、trust、stress、risk tolerance 和 skills
- stakeholders：不同社会角色的 trust、resistance、influence、stance
- environment：risk、pressure、opportunity、behavior、momentum 等指标

以及 `Ablation comparison`：

- Full Coupled：保留个人影响世界、世界影响个人
- No Individual Influence：关闭个人对社会/环境的影响
- No Society Influence：关闭社会/环境对个人的影响
- Isolated Baseline：关闭两个方向

---

## 方式 3：直接调用 API

启动 Web 后，可以直接调用 API：

### 创建 session

```bash
curl -X POST http://localhost:3000/api/session/start \
  -H "Content-Type: application/json" \
  -d '{
    "dilemma":"Should I leave my stable job for a startup?",
    "theme":"sci-fi",
    "maxTurns":3
  }'
```

使用 grounded preset scenario：

```bash
curl -X POST http://localhost:3000/api/session/start \
  -H "Content-Type: application/json" \
  -d '{
    "presetScenarioId":"ai_future_of_work",
    "maxTurns":2,
    "userContextPack":{
      "userGoal":"Become the internal AI transition lead without losing delivery credibility.",
      "currentPosition":"Senior IC on a product team under AI adoption pressure.",
      "riskPreference":"high",
      "timeHorizon":"9 months",
      "personalConstraints":["Must keep shipping core roadmap commitments."],
      "keyStakeholders":["manager","platform lead","teammates"]
    }
  }'
```

### 获取 session

```bash
curl http://localhost:3000/api/session/<sessionId>
```

### 获取 ablation report

```bash
curl http://localhost:3000/api/session/<sessionId>/ablation
```

### 选择分支

```bash
curl -X POST http://localhost:3000/api/session/choose \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId":"<sessionId>",
    "branchId":"<branchId>"
  }'
```

---

## Evaluation / 验证能力

项目内置了最小 evaluation harness，用来验证 core 是否还正常。

### 结构验证

```bash
npm run eval:mock
```

### 真实 provider 验证

```bash
npm run eval:core
```

### 轻量 smoke 模式

```bash
npm run eval:smoke
```

当前 evaluation 支持：

- 固定 scenario 集
- structural checks
- branch / society / summary timing metrics
- influence event linkage checks
- simulation state presence / turn alignment checks
- ablation report run count / event count / delta checks

可选环境变量：

```env
PARALLEL_AGENT_EVAL_MODE=smoke
PARALLEL_AGENT_EVAL_SCENARIOS=startup-offer
PARALLEL_AGENT_EVAL_MAX_SCENARIOS=1
PARALLEL_AGENT_EVAL_MAX_TURNS=1
```

---

## Society Simulation 模式

当前 society simulation 有两种策略：

### 1. `template`

特点：

- 更快
- 更稳定
- 质量较保守

### 2. `structured`

特点：

- 真实模型生成
- 社会角色更丰富
- 质量潜力更高
- 延迟更高

通过环境变量切换：

```env
PARALLEL_AGENT_SOCIETY_SIMULATOR=template
```

或

```env
PARALLEL_AGENT_SOCIETY_SIMULATOR=structured
```

当前默认：

- mock 模式下使用 `template`
- 真实 provider 下默认使用 `structured`

---

## 数据保存在哪里

本地 session 会保存到：

```text
.parallel-agent-data/sessions/
```
---

`Parallel Agent` 是一个把“复杂决策”变成“可交互平行未来探索”的引擎。

它当前最重要的价值，不是给你一个标准答案，而是帮助你看见：

> 如果你这样选，未来会怎样不同地展开。
