import type {
  BranchGenerator,
  SocietySimulator,
  SummaryGenerator,
  TurnSimulator,
} from "../../application/ports";
import { TurnOrchestrator } from "../../application/turn-orchestrator";
import { MockBranchGenerator } from "../branch/mock-branch-generator";
import { StructuredBranchGenerator } from "../branch/structured-branch-generator";
import {
  createJsonGenerationClient,
  getActiveProviderLabel,
} from "../llm/provider-factory";
import { FileSessionRepository } from "../persistence/file-session-repository";
import { StructuredSocietySimulator } from "../society/structured-society-simulator";
import { TemplateSocietySimulator } from "../society/template-society-simulator";
import { MockSummaryGenerator } from "../summary/mock-summary-generator";
import { StructuredSummaryGenerator } from "../summary/structured-summary-generator";
import { StructuredTurnSimulator } from "../turn/structured-turn-simulator";
import { NarrativeWorldModelProvider } from "../world-model/narrative-world-model-provider";

export function createWorldModelProvider(): NarrativeWorldModelProvider {
  return new NarrativeWorldModelProvider();
}

export function createBranchGenerator(): BranchGenerator {
  if (process.env.PARALLEL_AGENT_BRANCH_GENERATOR === "mock") {
    return new MockBranchGenerator();
  }

  const { client, providerLabel } = createJsonGenerationClient();
  return new StructuredBranchGenerator(client, providerLabel);
}

export function createSummaryGenerator(): SummaryGenerator {
  if (process.env.PARALLEL_AGENT_BRANCH_GENERATOR === "mock") {
    return new MockSummaryGenerator();
  }

  const { client, providerLabel } = createJsonGenerationClient();
  return new StructuredSummaryGenerator(client, providerLabel);
}

export function createSocietySimulator(): SocietySimulator {
  const strategy = process.env.PARALLEL_AGENT_SOCIETY_SIMULATOR ?? "structured";

  if (process.env.PARALLEL_AGENT_BRANCH_GENERATOR === "mock" || strategy === "template") {
    return new TemplateSocietySimulator();
  }

  if (strategy === "structured") {
    const { client, providerLabel } = createJsonGenerationClient();
    return new StructuredSocietySimulator(client, providerLabel);
  }

  throw new Error(
    `Unsupported PARALLEL_AGENT_SOCIETY_SIMULATOR "${strategy}". Use "structured" or "template".`,
  );
}

export function createTurnSimulator(): TurnSimulator | undefined {
  if (process.env.PARALLEL_AGENT_BRANCH_GENERATOR === "mock") {
    return undefined;
  }

  const strategy =
    process.env.PARALLEL_AGENT_TURN_SIMULATOR ??
    (process.env.PARALLEL_AGENT_MODEL_PROVIDER === "gemma" ||
    process.env.PARALLEL_AGENT_MODEL_PROVIDER === undefined
      ? "unified"
      : "legacy");

  if (strategy === "legacy") {
    return undefined;
  }

  if (strategy === "unified") {
    const { client, providerLabel } = createJsonGenerationClient();
    return new StructuredTurnSimulator(client, providerLabel);
  }

  throw new Error(
    `Unsupported PARALLEL_AGENT_TURN_SIMULATOR "${strategy}". Use "unified" or "legacy".`,
  );
}

export function createTurnOrchestrator(): TurnOrchestrator {
  return new TurnOrchestrator(
    createWorldModelProvider(),
    createBranchGenerator(),
    createSocietySimulator(),
    getActiveProviderLabel(),
    createTurnSimulator(),
  );
}

export function createSessionRepository(): FileSessionRepository {
  return new FileSessionRepository();
}
