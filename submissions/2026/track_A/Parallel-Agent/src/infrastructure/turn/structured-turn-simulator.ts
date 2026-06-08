import type { TurnSimulator } from "../../application/ports";
import {
  branchCommunitiesSchema,
  turnSimulationResultSchema,
} from "../../domain/schemas";
import type {
  Branch,
  BranchCommunity,
  BranchWorldDelta,
  InfluenceEvent,
  NativeToolCallRecord,
  TurnGenerationInput,
  TurnSimulationResult,
} from "../../domain/types";
import {
  buildFallbackInfluenceEvents,
  reconcileInfluenceEvents,
} from "../../domain/influence-events";
import type { JsonGenerationClient } from "../llm/anthropic-client";
import { AnthropicJsonClient } from "../llm/anthropic-client";
import { reconcileCommunitiesForBranches } from "../society/structured-society-simulator";
import { buildRealityTurnTool } from "./native-turn-tool";
import { buildTurnSimulationPrompt } from "./turn-simulation-prompts";

function unwrapTurnPayload(payload: unknown): unknown {
  if (!payload || typeof payload !== "object") {
    return payload;
  }

  const candidate = payload as {
    data?: unknown;
    result?: unknown;
    turn?: unknown;
    turnSimulation?: unknown;
    turnSimulationResult?: unknown;
  };

  return (
    candidate.turnSimulationResult ??
    candidate.turnSimulation ??
    candidate.turn ??
    candidate.result ??
    candidate.data ??
    payload
  );
}

function looksLikeCommunity(value: unknown): boolean {
  if (!value || typeof value !== "object") return false;
  const candidate = value as { agents?: unknown; branchId?: unknown };
  return typeof candidate.branchId === "string" && Array.isArray(candidate.agents);
}

function looksLikeInfluenceEvent(value: unknown): boolean {
  if (!value || typeof value !== "object") return false;
  const candidate = value as {
    branchId?: unknown;
    explanation?: unknown;
    sourceType?: unknown;
    targetType?: unknown;
  };
  return (
    typeof candidate.branchId === "string" &&
    typeof candidate.explanation === "string" &&
    typeof candidate.sourceType === "string" &&
    typeof candidate.targetType === "string"
  );
}

function findArray(
  payload: unknown,
  predicate: (value: unknown) => boolean,
): unknown[] | undefined {
  if (Array.isArray(payload)) {
    return payload.some(predicate) ? payload : undefined;
  }

  if (!payload || typeof payload !== "object") {
    return undefined;
  }

  const values = Object.values(payload);
  if (values.length > 0 && values.every(predicate)) {
    return values;
  }

  for (const value of values) {
    const nested: unknown[] | undefined = findArray(value, predicate);
    if (nested) return nested;
  }

  return undefined;
}

function normalizeActorType(value: unknown, fallback: string) {
  return value === "individual" || value === "society" || value === "environment"
    ? value
    : fallback;
}

function normalizeDimension(value: unknown) {
  return value === "trust" ||
    value === "risk" ||
    value === "behavior" ||
    value === "opportunity" ||
    value === "pressure"
    ? value
    : "pressure";
}

function normalizeDirection(value: unknown) {
  return value === "increase" || value === "decrease" || value === "redirect"
    ? value
    : "redirect";
}

function normalizeIntensity(value: unknown) {
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) return 0.5;
  return Math.min(1, Math.max(0, parsed));
}

function normalizeInfluenceEventsPayload(
  events: unknown,
  turnNumber: number,
): unknown[] {
  const eventArray = Array.isArray(events)
    ? events
    : findArray(events, looksLikeInfluenceEvent) ?? [];

  return eventArray
    .filter((event) => event && typeof event === "object")
    .map((event, index) => {
      const candidate = event as {
        branchId?: unknown;
        dimension?: unknown;
        direction?: unknown;
        explanation?: unknown;
        id?: unknown;
        intensity?: unknown;
        sourceId?: unknown;
        sourceType?: unknown;
        targetId?: unknown;
        targetType?: unknown;
        turn?: unknown;
      };
      const branchId =
        typeof candidate.branchId === "string" ? candidate.branchId : "b1";
      const sourceType = normalizeActorType(candidate.sourceType, "individual");
      const targetType = normalizeActorType(
        candidate.targetType,
        sourceType === "individual" ? "society" : "individual",
      );

      return {
        ...candidate,
        id:
          typeof candidate.id === "string"
            ? candidate.id
            : `ie-${turnNumber}-${branchId}-${index + 1}`,
        turn:
          typeof candidate.turn === "number" && Number.isInteger(candidate.turn)
            ? candidate.turn
            : turnNumber,
        branchId,
        sourceType,
        sourceId:
          typeof candidate.sourceId === "string"
            ? candidate.sourceId
            : sourceType === "individual"
              ? "observer"
              : "system",
        targetType,
        targetId:
          typeof candidate.targetId === "string"
            ? candidate.targetId
            : targetType === "individual"
              ? "observer"
              : "primary-stakeholder",
        dimension: normalizeDimension(candidate.dimension),
        direction: normalizeDirection(candidate.direction),
        intensity: normalizeIntensity(candidate.intensity),
        explanation:
          typeof candidate.explanation === "string"
            ? candidate.explanation
            : "This event captures a causal influence between the observer and surrounding reality.",
      };
    });
}

function normalizeTurnPayload(payload: unknown): unknown {
  if (!payload || typeof payload !== "object" || Array.isArray(payload)) {
    return payload;
  }

  const candidate = payload as {
    branchCommunities?: unknown;
    influenceEvents?: unknown;
    turnNumber?: unknown;
  };
  const turnNumber =
    typeof candidate.turnNumber === "number" && Number.isInteger(candidate.turnNumber)
      ? candidate.turnNumber
      : 1;

  return {
    ...candidate,
    branchCommunities: Array.isArray(candidate.branchCommunities)
      ? candidate.branchCommunities
      : findArray(candidate.branchCommunities, looksLikeCommunity) ?? [],
    influenceEvents: Array.isArray(candidate.influenceEvents)
      ? normalizeInfluenceEventsPayload(candidate.influenceEvents, turnNumber)
      : normalizeInfluenceEventsPayload(candidate.influenceEvents, turnNumber),
  };
}

function normalizeScores(result: TurnSimulationResult): TurnSimulationResult {
  const total = result.branches.reduce((sum, branch) => sum + branch.score, 0);

  if (total <= 0) {
    return {
      ...result,
      branches: result.branches.map((branch, _index, branches) => ({
        ...branch,
        score: Number((1 / branches.length).toFixed(2)),
      })),
    };
  }

  return {
    ...result,
    branches: result.branches.map((branch) => ({
      ...branch,
      score: Number((branch.score / total).toFixed(2)),
    })),
  };
}

function fallbackWorldDeltaForBranch(branch: Branch): BranchWorldDelta {
  return {
    branchId: branch.id,
    activatedConstraints:
      branch.riskProfile === "high"
        ? ["High-visibility choices raise execution pressure."]
        : branch.riskProfile === "low"
          ? ["Stability can reduce urgency and invite comparison risk."]
          : ["Hybrid moves require clear explanation to avoid ambiguity."],
    activatedOpportunities:
      branch.riskProfile === "high"
        ? ["Bold action can create visible momentum and new sponsors."]
        : branch.riskProfile === "low"
          ? ["Trust and continuity can compound into durable influence."]
          : ["Optionality can preserve access to multiple future paths."],
    pressureShift:
      branch.riskProfile === "high"
        ? "The world now tests whether boldness can become credible execution."
        : branch.riskProfile === "low"
          ? "The world now tests whether stability still carries ambition."
          : "The world now tests whether optionality is strategy or hesitation.",
  };
}

function reconcileWorldDeltas(
  branches: Branch[],
  deltas: BranchWorldDelta[],
): BranchWorldDelta[] {
  const deltasByBranchId = new Map(
    deltas.map((delta) => [delta.branchId, delta]),
  );

  return branches.map(
    (branch) => deltasByBranchId.get(branch.id) ?? fallbackWorldDeltaForBranch(branch),
  );
}

function parseCommunities(payload: unknown): BranchCommunity[] {
  return branchCommunitiesSchema.parse(payload);
}

function repairResult(result: TurnSimulationResult): TurnSimulationResult {
  const branchWorldDeltas = reconcileWorldDeltas(
    result.branches,
    result.branchWorldDeltas,
  );
  const branchCommunities = reconcileCommunitiesForBranches(
    parseCommunities(result.branchCommunities),
    result.branches,
  );
  const influenceEvents =
    result.influenceEvents.length > 0
      ? reconcileInfluenceEvents({
          branches: result.branches,
          branchCommunities,
          branchWorldDeltas,
          influenceEvents: result.influenceEvents,
          turnNumber: result.turnNumber,
        })
      : buildFallbackInfluenceEvents({
          branches: result.branches,
          branchCommunities,
          branchWorldDeltas,
          turnNumber: result.turnNumber,
        });

  return normalizeScores({
    ...result,
    branchWorldDeltas,
    branchCommunities,
    influenceEvents,
  });
}

function assertBranchLinkage(result: TurnSimulationResult): void {
  const branchIds = new Set(result.branches.map((branch) => branch.id));

  for (const delta of result.branchWorldDeltas) {
    if (!branchIds.has(delta.branchId)) {
      throw new Error(`Turn simulator referenced unknown delta branch id "${delta.branchId}".`);
    }
  }

  for (const community of result.branchCommunities) {
    if (!branchIds.has(community.branchId)) {
      throw new Error(
        `Turn simulator referenced unknown community branch id "${community.branchId}".`,
      );
    }
  }

  for (const event of result.influenceEvents) {
    if (!branchIds.has(event.branchId)) {
      throw new Error(`Turn simulator referenced unknown influence branch id "${event.branchId}".`);
    }
  }
}

function summarizeToolResult(result: TurnSimulationResult): string {
  return `turn=${result.turnNumber}, branches=${result.branches.length}, communities=${result.branchCommunities.length}, influenceEvents=${result.influenceEvents.length}`;
}

function buildValidatedToolCallRecords(params: {
  providerLabel: string;
  result: TurnSimulationResult;
  toolCalls: Array<{
    id?: string;
    name: string;
    arguments: unknown;
  }>;
}): NativeToolCallRecord[] {
  return params.toolCalls.map((toolCall, index) => ({
    id: toolCall.id ?? `native-tool-${params.result.turnNumber}-${index + 1}`,
    provider: params.providerLabel,
    toolName: toolCall.name,
    arguments: toolCall.arguments,
    status: "validated",
    resultSummary: summarizeToolResult(params.result),
  }));
}

function buildNativeToolPrompt(prompt: string): string {
  const [withoutJsonShape] = prompt.split("Return JSON with this exact top-level shape:");

  return `${withoutJsonShape
    .replace(
      "Simulate one decision turn as structured data. Return only valid JSON.\nDo not include Markdown, code fences, commentary, or extra top-level keys.",
      "Simulate one decision turn by calling the native function tool. Put the complete structured result object in the function arguments. Do not write free-text content.",
    )
    .trim()}

Native function calling instruction:
- Call simulate_reality_turn exactly once.
- Put turnNumber, branches, branchWorldDeltas, branchCommunities, and influenceEvents directly in the function arguments.
- Do not write JSON or prose in message content.
- Use exactly 3 branches, one world delta per branch, one community per branch, and at least 2 influenceEvents per branch.`;
}

export class StructuredTurnSimulator implements TurnSimulator {
  constructor(
    private readonly client: JsonGenerationClient = new AnthropicJsonClient(),
    private readonly providerLabel = "LLM",
  ) {}

  async simulate(input: TurnGenerationInput): Promise<TurnSimulationResult> {
    const basePrompt = buildTurnSimulationPrompt(input);
    const prompts = [
      basePrompt,
      `${basePrompt}\n\nYour previous answer was invalid. Return only strict JSON matching the required top-level shape. Include branchCommunities and influenceEvents for every branch.`,
    ];

    let lastError: unknown;

    for (const prompt of prompts) {
      try {
        const nativePrompt = buildNativeToolPrompt(prompt);
        const generation = this.client.generateJsonWithNativeTool
          ? await this.client.generateJsonWithNativeTool(
              nativePrompt,
              buildRealityTurnTool(),
            )
          : {
              jsonText: await this.client.generateJson(prompt),
              toolCalls: [],
            };
        const parsedJson = normalizeTurnPayload(
          unwrapTurnPayload(JSON.parse(generation.jsonText)),
        );
        const parsed = turnSimulationResultSchema.parse(parsedJson);
        const repaired = repairResult(parsed);
        assertBranchLinkage(repaired);
        return {
          ...repaired,
          toolCalls: buildValidatedToolCallRecords({
            providerLabel: this.providerLabel,
            result: repaired,
            toolCalls: generation.toolCalls,
          }),
        };
      } catch (error) {
        lastError = error;
      }
    }

    throw new Error(
      `${this.providerLabel} turn simulation failed after retry: ${
        lastError instanceof Error ? lastError.message : String(lastError)
      }`,
    );
  }
}
