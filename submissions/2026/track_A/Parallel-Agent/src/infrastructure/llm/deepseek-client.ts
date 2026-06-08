import type { JsonGenerationClient } from "./anthropic-client";

export type DeepSeekJsonClientOptions = {
  apiKey?: string;
  model?: string;
  maxTokens?: number;
  baseUrl?: string;
};

type DeepSeekResponse = {
  choices?: Array<{
    message?: {
      content?: string;
    };
  }>;
  error?: {
    message?: string;
  };
};

export class DeepSeekJsonClient implements JsonGenerationClient {
  private readonly apiKey: string;
  private readonly model: string;
  private readonly maxTokens: number;
  private readonly baseUrl: string;

  constructor(options: DeepSeekJsonClientOptions = {}) {
    const apiKey = options.apiKey ?? process.env.DEEPSEEK_API_KEY;

    if (!apiKey) {
      throw new Error(
        "DEEPSEEK_API_KEY is required to use DeepSeek structured generation.",
      );
    }

    this.apiKey = apiKey;
    this.model = options.model ?? process.env.DEEPSEEK_MODEL ?? "deepseek-chat";
    this.maxTokens = options.maxTokens ?? 2200;
    this.baseUrl = options.baseUrl ?? process.env.DEEPSEEK_BASE_URL ?? "https://api.deepseek.com";
  }

  async generateJson(prompt: string): Promise<string> {
    const response = await fetch(`${this.baseUrl}/chat/completions`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${this.apiKey}`,
      },
      body: JSON.stringify({
        model: this.model,
        temperature: 0.7,
        max_tokens: this.maxTokens,
        messages: [
          {
            role: "user",
            content: prompt,
          },
        ],
      }),
    });

    const payload = (await response.json()) as DeepSeekResponse;

    if (!response.ok) {
      throw new Error(
        payload.error?.message ??
          `DeepSeek request failed with status ${response.status}.`,
      );
    }

    const text = payload.choices?.[0]?.message?.content?.trim();

    if (!text) {
      throw new Error("DeepSeek returned an empty response.");
    }

    return stripCodeFence(text);
  }
}

function stripCodeFence(text: string): string {
  return text.replace(/^```(?:json)?\s*/i, "").replace(/\s*```$/, "").trim();
}
