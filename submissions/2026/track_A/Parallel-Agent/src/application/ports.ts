import type {
  BranchCommunity,
  SessionSummary,
  SocietySimulationInput,
  SessionState,
  TurnDraft,
  TurnGenerationInput,
  TurnSimulationResult,
  WorldContext,
} from "../domain/types";

export interface WorldModelProvider {
  getContext(session: SessionState): Promise<WorldContext>;
}

export interface BranchGenerator {
  generate(input: TurnGenerationInput): Promise<TurnDraft>;
}

export interface SocietySimulator {
  simulate(input: SocietySimulationInput): Promise<BranchCommunity[]>;
}

export interface TurnSimulator {
  simulate(input: TurnGenerationInput): Promise<TurnSimulationResult>;
}

export interface SummaryGenerator {
  generate(session: SessionState): Promise<SessionSummary>;
}

export interface SessionRepository {
  save(session: SessionState): Promise<void>;
  load(sessionId: string): Promise<SessionState | null>;
  list(): Promise<SessionState[]>;
}
