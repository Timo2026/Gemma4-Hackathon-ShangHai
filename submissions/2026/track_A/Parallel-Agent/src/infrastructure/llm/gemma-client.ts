import type {
  JsonGenerationClient,
  NativeJsonGenerationResult,
  NativeJsonToolCall,
  NativeJsonToolDefinition,
} from "./anthropic-client";

export type GemmaRuntime = "huggingface" | "openai-compatible" | "ollama";

export type GemmaJsonClientOptions = {
  apiKey?: string;
  baseUrl?: string;
  maxTokens?: number;
  model?: string;
  runtime?: GemmaRuntime;
  temperature?: number;
};

type OpenAICompatibleChatResponse = {
  choices?: Array<{
    message?: {
      content?: string;
      tool_calls?: Array<{
        id?: string;
        function?: {
          name?: string;
          arguments?: string | Record<string, unknown>;
        };
      }>;
    };
  }>;
  error?: {
    message?: string;
  };
};

type OllamaChatResponse = {
  message?: {
    content?: string;
    tool_calls?: Array<{
      id?: string;
      function?: {
        name?: string;
        arguments?: string | Record<string, unknown>;
      };
    }>;
  };
  error?: string;
};

function parseNumberEnv(value: string | undefined): number | undefined {
  if (!value) return undefined;

  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : undefined;
}

function stripCodeFence(text: string): string {
  return text.replace(/^```(?:json)?\s*/i, "").replace(/\s*```$/, "").trim();
}

function parseToolArguments(argumentsPayload: unknown): unknown {
  if (typeof argumentsPayload === "string") {
    return JSON.parse(argumentsPayload);
  }

  return argumentsPayload;
}

function serializeToolArguments(argumentsPayload: unknown): string {
  if (typeof argumentsPayload === "string") {
    return argumentsPayload;
  }

  return JSON.stringify(argumentsPayload);
}

function normalizeNativeToolCalls(
  toolCalls: Array<{
    id?: string;
    function?: {
      name?: string;
      arguments?: string | Record<string, unknown>;
    };
  }> | undefined,
): NativeJsonToolCall[] {
  const normalized: NativeJsonToolCall[] = [];

  for (const [index, toolCall] of (toolCalls ?? []).entries()) {
    const name = toolCall.function?.name;

    if (!name) {
      continue;
    }

    normalized.push({
      id: toolCall.id ?? `tool-call-${index + 1}`,
      name,
      arguments: parseToolArguments(toolCall.function?.arguments ?? {}),
    });
  }

  return normalized;
}

function describeFetchFailure(error: unknown): string {
  if (!(error instanceof Error)) {
    return String(error);
  }

  const cause = error.cause as
    | {
        code?: string;
        message?: string;
        name?: string;
      }
    | undefined;
  const causeDetails = cause
    ? ` cause=${cause.name ?? "Error"} code=${cause.code ?? "unknown"} message=${cause.message ?? "unknown"}`
    : "";
  const networkHint =
    cause?.code === "ENOTFOUND"
      ? " DNS lookup failed. Check network/DNS access to Hugging Face."
      : cause?.code === "ECONNRESET"
        ? " The connection was reset before a response was received. This is usually a network, proxy, firewall, or remote routing issue."
        : "";

  return `${error.name}: ${error.message}.${causeDetails}${networkHint}`;
}

function inferRuntime(value: GemmaRuntime | undefined): GemmaRuntime {
  if (value) return value;
  if (process.env.GEMMA_RUNTIME) return process.env.GEMMA_RUNTIME as GemmaRuntime;
  return "ollama";
}

function assertSupportedRuntime(runtime: string): asserts runtime is GemmaRuntime {
  if (
    runtime !== "huggingface" &&
    runtime !== "openai-compatible" &&
    runtime !== "ollama"
  ) {
    throw new Error(
      `Unsupported GEMMA_RUNTIME "${runtime}". Use "huggingface", "openai-compatible", or "ollama".`,
    );
  }
}

export function getGemmaRuntimeLabel(): string {
  const runtime = inferRuntime(undefined);
  assertSupportedRuntime(runtime);

  const defaultModel =
    runtime === "ollama" ? "gemma4:latest" : "google/gemma-4-26B-A4B-it:novita";
  return `Gemma 4 (${process.env.GEMMA_MODEL ?? defaultModel}, ${runtime})`;
}

export class GemmaJsonClient implements JsonGenerationClient {
  private readonly apiKey?: string;
  private readonly baseUrl: string;
  private readonly maxTokens: number;
  private readonly model: string;
  private readonly runtime: GemmaRuntime;
  private readonly temperature: number;

  constructor(options: GemmaJsonClientOptions = {}) {
    const runtime = inferRuntime(options.runtime);
    assertSupportedRuntime(runtime);

    this.runtime = runtime;
    this.apiKey = options.apiKey ?? process.env.GEMMA_API_KEY ?? process.env.HF_TOKEN;
    this.baseUrl = this.resolveBaseUrl(options.baseUrl).replace(/\/$/, "");
    this.maxTokens =
      options.maxTokens ??
      parseNumberEnv(process.env.GEMMA_MAX_TOKENS) ??
      (this.runtime === "ollama" ? 6000 : 2200);
    this.model = options.model ?? process.env.GEMMA_MODEL ?? this.defaultModel();
    this.temperature =
      options.temperature ?? parseNumberEnv(process.env.GEMMA_TEMPERATURE) ?? 0.7;

    if (this.runtime === "huggingface" && !this.apiKey) {
      throw new Error(
        "HF_TOKEN or GEMMA_API_KEY is required to use Gemma 4 through Hugging Face Router.",
      );
    }
  }

  async generateJson(prompt: string): Promise<string> {
    if (this.runtime === "ollama") {
      return this.generateWithOllama(prompt);
    }

    return this.generateWithOpenAICompatible(prompt);
  }

  async generateJsonWithNativeTool(
    prompt: string,
    tool: NativeJsonToolDefinition,
  ): Promise<NativeJsonGenerationResult> {
    if (this.runtime === "ollama") {
      return this.generateWithOllamaTool(prompt, tool);
    }

    return this.generateWithOpenAICompatibleTool(prompt, tool);
  }

  private defaultModel(): string {
    return this.runtime === "ollama"
      ? "gemma4:latest"
      : "google/gemma-4-26B-A4B-it:novita";
  }

  private resolveBaseUrl(baseUrl: string | undefined): string {
    if (baseUrl) return baseUrl;
    if (process.env.GEMMA_BASE_URL) return process.env.GEMMA_BASE_URL;

    if (this.runtime === "huggingface") {
      return "https://router.huggingface.co/v1";
    }

    if (this.runtime === "openai-compatible") {
      return "http://localhost:1234/v1";
    }

    return process.env.OLLAMA_BASE_URL ?? "http://localhost:11434";
  }

  private async generateWithOpenAICompatible(prompt: string): Promise<string> {
    let response: Response;

    try {
      response = await fetch(`${this.baseUrl}/chat/completions`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(this.apiKey ? { Authorization: `Bearer ${this.apiKey}` } : {}),
        },
        body: JSON.stringify({
          model: this.model,
          temperature: Math.min(this.temperature, 0.1),
          max_tokens: this.maxTokens,
          stream: false,
          messages: [
            {
              role: "system",
              content:
                "You are Gemma 4 powering Parallel Agent. Return strict JSON only. Do not include Markdown, code fences, or commentary.",
            },
            {
              role: "user",
              content: prompt,
            },
          ],
        }),
      });
    } catch (error) {
      throw new Error(
        `Gemma 4 request failed. Confirm GEMMA_RUNTIME="${this.runtime}", GEMMA_BASE_URL="${this.baseUrl}", and GEMMA_MODEL="${this.model}". ${
          describeFetchFailure(error)
        }`,
      );
    }

    const payload = (await response.json().catch(() => ({}))) as
      OpenAICompatibleChatResponse;

    if (!response.ok) {
      throw new Error(
        payload.error?.message ??
          `Gemma 4 request failed with status ${response.status}. Check GEMMA_BASE_URL="${this.baseUrl}" and GEMMA_MODEL="${this.model}".`,
      );
    }

    const text = payload.choices?.[0]?.message?.content?.trim();

    if (!text) {
      throw new Error("Gemma 4 returned an empty response.");
    }

    return stripCodeFence(text);
  }

  private async generateWithOpenAICompatibleTool(
    prompt: string,
    tool: NativeJsonToolDefinition,
  ): Promise<NativeJsonGenerationResult> {
    let response: Response;

    try {
      response = await fetch(`${this.baseUrl}/chat/completions`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(this.apiKey ? { Authorization: `Bearer ${this.apiKey}` } : {}),
        },
        body: JSON.stringify({
          model: this.model,
          temperature: this.temperature,
          max_tokens: this.maxTokens,
          stream: false,
          tools: [
            {
              type: "function",
              function: tool,
            },
          ],
          tool_choice: {
            type: "function",
            function: {
              name: tool.name,
            },
          },
          messages: [
            {
              role: "system",
              content:
                "You are Gemma 4 powering Parallel Agent. Use the provided native function call. Do not answer in free text.",
            },
            {
              role: "user",
              content: prompt,
            },
          ],
        }),
      });
    } catch (error) {
      throw new Error(
        `Gemma 4 native tool request failed. Confirm GEMMA_RUNTIME="${this.runtime}", GEMMA_BASE_URL="${this.baseUrl}", and GEMMA_MODEL="${this.model}". ${
          describeFetchFailure(error)
        }`,
      );
    }

    const payload = (await response.json().catch(() => ({}))) as
      OpenAICompatibleChatResponse;

    if (!response.ok) {
      throw new Error(
        payload.error?.message ??
          `Gemma 4 native tool request failed with status ${response.status}. Check GEMMA_BASE_URL="${this.baseUrl}" and GEMMA_MODEL="${this.model}".`,
      );
    }

    const toolCalls = normalizeNativeToolCalls(
      payload.choices?.[0]?.message?.tool_calls,
    );
    const selectedToolCall = toolCalls.find((toolCall) => toolCall.name === tool.name);

    if (!selectedToolCall) {
      throw new Error(`Gemma 4 did not call required native tool "${tool.name}".`);
    }

    return {
      jsonText: serializeToolArguments(selectedToolCall.arguments),
      toolCalls,
    };
  }

  private async generateWithOllama(prompt: string): Promise<string> {
    let response: Response;

    try {
      response = await fetch(`${this.baseUrl}/api/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(this.apiKey ? { Authorization: `Bearer ${this.apiKey}` } : {}),
        },
        body: JSON.stringify({
          model: this.model,
          stream: false,
          format: "json",
          options: {
            num_predict: this.maxTokens,
            temperature: Math.min(this.temperature, 0.1),
          },
          messages: [
            {
              role: "system",
              content:
                "You are Gemma 4 powering Parallel Agent. Return strict JSON only. Do not include Markdown, code fences, or commentary.",
            },
            {
              role: "user",
              content: prompt,
            },
          ],
        }),
      });
    } catch (error) {
      throw new Error(
        `Gemma Ollama request failed. Confirm Ollama is running at OLLAMA_BASE_URL="${this.baseUrl}" and the model "${this.model}" is available. ${
          describeFetchFailure(error)
        }`,
      );
    }

    const payload = (await response.json().catch(() => ({}))) as OllamaChatResponse;

    if (!response.ok) {
      throw new Error(
        payload.error ??
          `Gemma Ollama request failed with status ${response.status}. Check OLLAMA_BASE_URL="${this.baseUrl}" and GEMMA_MODEL="${this.model}".`,
      );
    }

    const text = payload.message?.content?.trim();

    if (!text) {
      throw new Error("Gemma Ollama returned an empty response.");
    }

    return stripCodeFence(text);
  }

  private async generateWithOllamaTool(
    prompt: string,
    tool: NativeJsonToolDefinition,
  ): Promise<NativeJsonGenerationResult> {
    let response: Response;

    try {
      response = await fetch(`${this.baseUrl}/api/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(this.apiKey ? { Authorization: `Bearer ${this.apiKey}` } : {}),
        },
        body: JSON.stringify({
          model: this.model,
          stream: false,
          think: false,
          options: {
            num_predict: this.maxTokens,
            temperature: Math.min(this.temperature, 0.1),
          },
          tools: [
            {
              type: "function",
              function: tool,
            },
          ],
          messages: [
            {
              role: "system",
              content:
                `You are Gemma 4 powering Parallel Agent. You must call the native function "${tool.name}" exactly once. Do not answer in free text.`,
            },
            {
              role: "user",
              content: prompt,
            },
          ],
        }),
      });
    } catch (error) {
      throw new Error(
        `Gemma Ollama native tool request failed. Confirm Ollama is running at OLLAMA_BASE_URL="${this.baseUrl}" and the model "${this.model}" is available. ${
          describeFetchFailure(error)
        }`,
      );
    }

    const payload = (await response.json().catch(() => ({}))) as OllamaChatResponse;

    if (!response.ok) {
      throw new Error(
        payload.error ??
          `Gemma Ollama native tool request failed with status ${response.status}. Check OLLAMA_BASE_URL="${this.baseUrl}" and GEMMA_MODEL="${this.model}".`,
      );
    }

    const toolCalls = normalizeNativeToolCalls(payload.message?.tool_calls);
    const selectedToolCall = toolCalls.find((toolCall) => toolCall.name === tool.name);

    if (!selectedToolCall) {
      throw new Error(`Gemma Ollama did not call required native tool "${tool.name}".`);
    }

    return {
      jsonText: serializeToolArguments(selectedToolCall.arguments),
      toolCalls,
    };
  }
}
