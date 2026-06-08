import type { BranchGenerator } from "../../application/ports";
import { turnDraftSchema } from "../../domain/schemas";
import type { TurnDraft, TurnGenerationInput } from "../../domain/types";
import type { JsonGenerationClient } from "../llm/anthropic-client";
import { AnthropicJsonClient } from "../llm/anthropic-client";
import { buildClaudeBranchGenerationPrompt } from "./branch-generation-prompts";

function normalizeScores(draft: TurnDraft): TurnDraft {
  const total = draft.branches.reduce((sum, branch) => sum + branch.score, 0);

  if (total <= 0) {
    return {
      ...draft,
      branches: draft.branches.map((branch, _index, branches) => ({
        ...branch,
        score: Number((1 / branches.length).toFixed(2)),
      })),
    };
  }

  return {
    ...draft,
    branches: draft.branches.map((branch) => ({
      ...branch,
      score: Number((branch.score / total).toFixed(2)),
    })),
  };
}

function assertBranchLinkage(draft: TurnDraft): void {
  const branchIds = new Set(draft.branches.map((branch) => branch.id));

  for (const delta of draft.branchWorldDeltas) {
    if (!branchIds.has(delta.branchId)) {
      throw new Error(`World delta references unknown branch id "${delta.branchId}".`);
    }
  }
}

export class StructuredBranchGenerator implements BranchGenerator {
  constructor(
    private readonly client: JsonGenerationClient = new AnthropicJsonClient(),
    private readonly providerLabel = "LLM",
  ) {}

  async generate(input: TurnGenerationInput): Promise<TurnDraft> {
    const basePrompt = buildClaudeBranchGenerationPrompt(input);
    const prompts = [
      basePrompt,
      `${basePrompt}\n\nYour previous answer was invalid. Return only strict JSON matching the required shape. Do not include Markdown, code fences, or commentary.`,
    ];

    let lastError: unknown;

    for (const prompt of prompts) {
      try {
        const responseText = await this.client.generateJson(prompt);
        const parsedJson = JSON.parse(responseText);
        const parsed = turnDraftSchema.parse(parsedJson);
        assertBranchLinkage(parsed);
        return normalizeScores(parsed);
      } catch (error) {
        lastError = error;
      }
    }

    throw new Error(
      `${this.providerLabel} structured generation failed after retry: ${
        lastError instanceof Error ? lastError.message : String(lastError)
      }`,
    );
  }
}
