import { AnthropicJsonClient, type JsonGenerationClient } from "./anthropic-client";
import { DeepSeekJsonClient } from "./deepseek-client";
import { GemmaJsonClient, getGemmaRuntimeLabel } from "./gemma-client";

export function getActiveProviderLabel(): string {
  const provider = process.env.PARALLEL_AGENT_MODEL_PROVIDER ?? "gemma";

  if (process.env.PARALLEL_AGENT_BRANCH_GENERATOR === "mock") {
    return "Mock";
  }

  if (provider === "anthropic") return "Anthropic";
  if (provider === "deepseek") return "DeepSeek";
  if (provider === "gemma") return getGemmaRuntimeLabel();

  return provider;
}

export function createJsonGenerationClient(): {
  client: JsonGenerationClient;
  providerLabel: string;
} {
  const provider = process.env.PARALLEL_AGENT_MODEL_PROVIDER ?? "gemma";

  if (provider === "anthropic") {
    return {
      client: new AnthropicJsonClient(),
      providerLabel: "Anthropic",
    };
  }

  if (provider === "deepseek") {
    return {
      client: new DeepSeekJsonClient(),
      providerLabel: "DeepSeek",
    };
  }

  if (provider === "gemma") {
    return {
      client: new GemmaJsonClient(),
      providerLabel: getGemmaRuntimeLabel(),
    };
  }

  throw new Error(
    `Unsupported PARALLEL_AGENT_MODEL_PROVIDER "${provider}". Use "gemma", "deepseek", or "anthropic".`,
  );
}
