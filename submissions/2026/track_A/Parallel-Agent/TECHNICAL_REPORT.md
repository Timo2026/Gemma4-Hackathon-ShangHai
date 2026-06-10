# Parallel Agent Technical Report

Team: VirtuOasis  
Track: A - AI Agent  
Project: Parallel Agent  
Core model: Gemma 4 via local Ollama

## 1. Project Summary

Parallel Agent is a multi-turn decision simulation agent. A user enters a real dilemma, Gemma 4 generates three parallel future branches, the user collapses one branch into the canonical path, and the system repeats the process until the session reaches the configured turn limit. The product focuses on complex career and life decisions where the useful output is not one recommendation, but a visible comparison of possible futures, social reactions, risks, and downstream consequences.

The submitted version is a Next.js + TypeScript full-stack app with:

- Web UI for session start, branch observation, collapse, memory trace, and final summary.
- API routes for session start, branch choice, session fetch, and ablation reports.
- Headless core for turn orchestration, memory, branch generation, influence events, simulation-state reduction, and evaluation.
- Local file persistence under `.parallel-agent-data/sessions/`.

## 2. Why Gemma 4

The hackathon demo uses `gemma4:latest` through Ollama. In the local validation environment, Ollama reports the model as Gemma 4 family with tools support. This deployment path was chosen for three reasons:

1. Local execution keeps private decision context on the user's machine.
2. Gemma 4 supports native tool calling, which lets the model return structured function arguments instead of relying on free-text parsing.
3. The local Ollama runtime is simple for judges to reproduce: install dependencies, run/pull `gemma4:latest`, and start the app.

The model is used as a structured reality simulator. Parallel Agent keeps deterministic control over validation, score normalization, branch linkage checks, session memory, and state reduction.

## 3. Architecture

Parallel Agent has two layers:

- Generative layer: Gemma 4 produces one decision turn through a native function call.
- Deterministic layer: TypeScript code validates the tool arguments, repairs safe structural gaps, normalizes scores, records memory, applies collapse, archives shadow timelines, and updates the simulation state.

The main flow is:

```text
User dilemma
  -> createSession()
  -> TurnOrchestrator.generateTurn()
  -> Gemma 4 native tool call: simulate_reality_turn(...)
  -> Zod validation + repairResult()
  -> UI renders branches
  -> user chooses a branch
  -> applyCollapse()
  -> encodeEntanglement()
  -> applyInfluenceEventsToSimulationState()
  -> persist session
  -> generate summary when complete
```

Key implementation files:

- `src/infrastructure/llm/gemma-client.ts`: Gemma 4 Ollama and OpenAI-compatible clients.
- `src/infrastructure/turn/native-turn-tool.ts`: native function schema for `simulate_reality_turn`.
- `src/infrastructure/turn/structured-turn-simulator.ts`: calls Gemma 4 through the native function path and validates returned arguments.
- `src/application/turn-orchestrator.ts`: coordinates generation, collapse, trace, simulation state, and tool-call persistence.
- `src/domain/types.ts`: session state, branch, memory, influence event, and tool-call record types.

## 4. Native Function Calling

Parallel Agent uses one native function for the core turn:

```text
simulate_reality_turn
```

The tool arguments contain:

- `turnNumber`
- `branches`
- `branchWorldDeltas`
- `branchCommunities`
- `influenceEvents`

Gemma 4 is instructed to call this function exactly once for each turn. The returned `tool_calls[].function.arguments` becomes the source of truth for the generated turn. The app does not trust the raw arguments blindly; it validates them with Zod schemas and then runs deterministic repair and linkage checks.

The tool-call record is stored as:

```ts
type NativeToolCallRecord = {
  id: string
  provider: string
  toolName: string
  arguments: unknown
  status: "requested" | "validated" | "rejected"
  resultSummary: string
}
```

The records are available in:

- `pendingTurn.toolCalls` before the user collapses a branch.
- `session.toolCalls` after the turn is collapsed and persisted.
- The Web UI section "Gemma Native Function Calling".
- Evaluation output, for example `toolCalls=simulate_reality_turn:validated`.

## 5. Agent Memory

Parallel Agent keeps compact memory instead of a full transcript:

- `canonicalPath`: selected branches, one per collapsed turn.
- `shadowTimelines`: unselected branches archived by turn.
- `quantumTrace`: short residue entries extracted from each collapse.
- `userPersona`: evolving risk tolerance, emotional state, primary value, wins, and wounds.
- `simulationState`: individual, stakeholder, and environment metrics.
- `influenceEvents`: causal links between individual, society, and environment.
- `toolCalls`: native function-call records.

This memory is small enough to feed into later turns while still preserving causal continuity.

## 6. Tool Calling and Multi-Step Planning

The model's native tool call generates candidate realities. Parallel Agent then executes local deterministic tools:

- schema validation
- branch score normalization
- branch/world/community linkage repair
- influence-event reconciliation
- collapse handling
- quantum trace encoding
- simulation-state reducer
- ablation report generation

This gives the agent a clear split: Gemma 4 proposes structured futures, while local code enforces consistency and applies state transitions.

## 7. Validation

The current local validation results:

```text
npm ci
npm run check
npm run web:build
npm run eval:mock
npm run gemma:smoke
npm run eval:gemma:smoke
```

Validated behavior:

- TypeScript check passes.
- Next.js production build passes.
- Mock evaluation passes all scenarios.
- Gemma 4 smoke test passes.
- Gemma 4 smoke evaluation completes one real turn with structural checks passing.
- Web API can start a session, return branches, collapse a selected branch, update memory, and produce a final summary.

## 8. Demo Notes

Recommended screenshot/recording flow:

1. Run `npm run eval:gemma:smoke` and capture the terminal line showing `toolCalls=simulate_reality_turn:validated`.
2. Run `npm run web:gemma`.
3. Open `http://localhost:3000`.
4. Start a session with the AI future-of-work preset or a custom dilemma.
5. Capture the "Gemma Native Function Calling" section.
6. Choose a branch and show the persisted tool call, canonical path, quantum trace, simulation state, and summary.

The final video must stay under five minutes.
