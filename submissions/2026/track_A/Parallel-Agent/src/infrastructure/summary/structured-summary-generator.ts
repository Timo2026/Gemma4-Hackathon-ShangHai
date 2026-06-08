import type { SummaryGenerator } from "../../application/ports";
import { sessionSummarySchema } from "../../domain/schemas";
import type { SessionState, SessionSummary } from "../../domain/types";
import {
  AnthropicJsonClient,
  type JsonGenerationClient,
} from "../llm/anthropic-client";
import { buildStructuredSummaryPrompt } from "./summary-prompts";

export class StructuredSummaryGenerator implements SummaryGenerator {
  constructor(
    private readonly client: JsonGenerationClient = new AnthropicJsonClient(),
    private readonly providerLabel = "LLM",
  ) {}

  async generate(session: SessionState): Promise<SessionSummary> {
    const basePrompt = buildStructuredSummaryPrompt(session);
    const prompts = [
      basePrompt,
      `${basePrompt}\n\nYour previous answer was invalid. Return only strict JSON matching the required shape. Do not include Markdown, code fences, or commentary.`,
    ];

    let lastError: unknown;

    for (const prompt of prompts) {
      try {
        const responseText = await this.client.generateJson(prompt);
        const parsedJson = JSON.parse(responseText);
        return sessionSummarySchema.parse(parsedJson);
      } catch (error) {
        lastError = error;
      }
    }

    throw new Error(
      `${this.providerLabel} summary generation failed after retry: ${
        lastError instanceof Error ? lastError.message : String(lastError)
      }`,
    );
  }
}
