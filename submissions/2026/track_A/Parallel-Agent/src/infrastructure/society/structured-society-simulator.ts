import type { SocietySimulator } from "../../application/ports";
import { branchCommunitiesSchema } from "../../domain/schemas";
import type {
  Branch,
  BranchCommunity,
  SocietySimulationInput,
} from "../../domain/types";
import type { JsonGenerationClient } from "../llm/anthropic-client";
import { AnthropicJsonClient } from "../llm/anthropic-client";
import { buildStructuredSocietyPrompt } from "./structured-society-prompts";

function looksLikeCommunity(value: unknown): boolean {
  if (!value || typeof value !== "object") {
    return false;
  }

  const candidate = value as {
    agents?: unknown;
    branchId?: unknown;
  };

  return typeof candidate.branchId === "string" && Array.isArray(candidate.agents);
}

function findCommunitiesArray(payload: unknown): unknown[] | undefined {
  if (Array.isArray(payload)) {
    return payload.some(looksLikeCommunity) ? payload : undefined;
  }

  if (!payload || typeof payload !== "object") {
    return undefined;
  }

  const values = Object.values(payload);

  if (values.length > 0 && values.every(looksLikeCommunity)) {
    return values;
  }

  for (const value of values) {
    const nested = findCommunitiesArray(value);
    if (nested) {
      return nested;
    }
  }

  return undefined;
}

function unwrapCommunitiesPayload(payload: unknown): unknown {
  if (Array.isArray(payload)) {
    return payload;
  }

  if (!payload || typeof payload !== "object") {
    return payload;
  }

  const candidate = payload as {
    branchCommunities?: unknown;
    communities?: unknown;
    data?: unknown;
    result?: unknown;
  };

  return (
    findCommunitiesArray(payload) ??
    candidate.branchCommunities ??
    candidate.communities ??
    candidate.data ??
    candidate.result ??
    payload
  );
}

function assertBranchLinkage(
  communities: BranchCommunity[],
  input: SocietySimulationInput,
): void {
  const branchIds = new Set(input.branches.map((branch) => branch.id));

  if (communities.length !== input.branches.length) {
    throw new Error(
      `Society simulator returned ${communities.length} communities for ${input.branches.length} branches.`,
    );
  }

  for (const community of communities) {
    if (!branchIds.has(community.branchId)) {
      throw new Error(
        `Society simulator referenced unknown branch id "${community.branchId}".`,
      );
    }
  }
}

export function fallbackCommunityForBranch(branch: Branch): BranchCommunity {
  return {
    branchId: branch.id,
    agents: [
      {
        role: "Primary Stakeholder",
        stance: branch.riskProfile === "high" ? "uncertain" : "supportive",
        motivation: "Wants the user's decision to remain credible and sustainable.",
        influence: 0.75,
        reaction:
          branch.riskProfile === "high"
            ? "Sees the upside, but worries about execution pressure and volatility."
            : "Sees the path as easier to support if it still creates visible progress.",
      },
      {
        role: "Peer Observer",
        stance: branch.riskProfile === "low" ? "resistant" : "neutral",
        motivation: "Judges the move by whether it changes the user's trajectory.",
        influence: 0.55,
        reaction:
          branch.riskProfile === "low"
            ? "Questions whether the safer move will create enough momentum."
            : "Waits to see whether the move becomes real leverage or just intention.",
      },
      {
        role: "Personal Support System",
        stance: "supportive",
        motivation: "Wants growth without avoidable regret.",
        influence: 0.65,
        reaction: "Supports the decision while watching for second-order stress.",
      },
    ],
    socialDynamics:
      branch.riskProfile === "high"
        ? "The branch creates excitement and scrutiny at the same time."
        : branch.riskProfile === "low"
          ? "The branch creates stability, but also questions about ambition."
          : "The branch creates optionality, but asks others to tolerate ambiguity.",
    dominantNarrative:
      branch.riskProfile === "high"
        ? "People read this as a momentum-first bet that must quickly prove itself."
        : branch.riskProfile === "low"
          ? "People read this as a stability-first move that still needs visible progress."
          : "People read this as a bridge strategy that preserves agency under uncertainty.",
  };
}

export function reconcileCommunities(
  communities: BranchCommunity[],
  input: SocietySimulationInput,
): BranchCommunity[] {
  return reconcileCommunitiesForBranches(communities, input.branches);
}

export function reconcileCommunitiesForBranches(
  communities: BranchCommunity[],
  branches: Branch[],
): BranchCommunity[] {
  const communitiesByBranchId = new Map(
    communities.map((community) => [community.branchId, community]),
  );

  return branches.map(
    (branch) => communitiesByBranchId.get(branch.id) ?? fallbackCommunityForBranch(branch),
  );
}

export class StructuredSocietySimulator implements SocietySimulator {
  constructor(
    private readonly client: JsonGenerationClient = new AnthropicJsonClient(),
    private readonly providerLabel = "LLM",
  ) {}

  async simulate(input: SocietySimulationInput): Promise<BranchCommunity[]> {
    const basePrompt = buildStructuredSocietyPrompt(input);
    const prompts = [
      basePrompt,
      `${basePrompt}\n\nYour previous answer was invalid. Return only strict JSON matching the required shape. Do not include Markdown, code fences, or commentary.`,
    ];

    let lastError: unknown;

    for (const prompt of prompts) {
      try {
        const responseText = await this.client.generateJson(prompt);
        const parsedJson = JSON.parse(responseText);
        const parsed = branchCommunitiesSchema.parse(
          unwrapCommunitiesPayload(parsedJson),
        );
        const reconciled = reconcileCommunities(parsed, input);
        assertBranchLinkage(reconciled, input);
        return reconciled;
      } catch (error) {
        lastError = error;
      }
    }

    throw new Error(
      `${this.providerLabel} society simulation failed after retry: ${
        lastError instanceof Error ? lastError.message : String(lastError)
      }`,
    );
  }
}
