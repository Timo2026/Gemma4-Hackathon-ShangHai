import { buildAblationReport } from "../../domain/ablation-report";
import { createSession } from "../../domain/session-engine";
import type {
  AblationReport,
  OutputLanguage,
  PresetScenarioId,
  SessionState,
  Theme,
  UserAuthoredActionInput,
  UserContextPackInput,
  UserProvidedDataInput,
} from "../../domain/types";
import {
  createSessionRepository,
  createSummaryGenerator,
  createTurnOrchestrator,
} from "../../infrastructure/runtime/create-runtime";

export async function startWebSession(params: {
  dilemma?: string;
  theme?: Theme;
  language?: OutputLanguage;
  maxTurns?: number;
  presetScenarioId?: PresetScenarioId;
  userContextPack?: UserContextPackInput;
  userProvidedData?: UserProvidedDataInput;
}): Promise<SessionState> {
  const repository = createSessionRepository();
  const orchestrator = createTurnOrchestrator();

  const session = createSession({
    dilemma: params.dilemma,
    theme: params.theme,
    language: params.language,
    maxTurns: params.maxTurns,
    presetScenarioId: params.presetScenarioId,
    userContextPack: params.userContextPack,
    userProvidedData: params.userProvidedData,
  });

  const turn = await orchestrator.generateTurn(session);
  const sessionWithPendingTurn: SessionState = {
    ...session,
    pendingTurn: turn,
  };

  await repository.save(sessionWithPendingTurn);
  return sessionWithPendingTurn;
}

export async function getWebSession(sessionId: string): Promise<SessionState | null> {
  const repository = createSessionRepository();
  return repository.load(sessionId);
}

export async function getWebAblationReport(
  sessionId: string,
): Promise<AblationReport | null> {
  const repository = createSessionRepository();
  const session = await repository.load(sessionId);

  if (!session) {
    return null;
  }

  return buildAblationReport(session);
}

export async function chooseWebBranch(params: {
  sessionId: string;
  branchId: string;
}): Promise<SessionState> {
  return chooseWebTurnAction({
    sessionId: params.sessionId,
    branchId: params.branchId,
  });
}

export async function chooseWebTurnAction(params: {
  sessionId: string;
  branchId?: string;
  authoredAction?: UserAuthoredActionInput;
}): Promise<SessionState> {
  const repository = createSessionRepository();
  const session = await repository.load(params.sessionId);

  if (!session) {
    throw new Error(`Session "${params.sessionId}" was not found.`);
  }

  const pendingTurn = session.pendingTurn;

  if (!pendingTurn) {
    throw new Error(`Session "${params.sessionId}" has no pending turn.`);
  }

  const orchestrator = createTurnOrchestrator();
  let nextSession: SessionState;

  if (params.authoredAction) {
    if (!params.authoredAction.rawInput.trim()) {
      throw new Error("authoredAction.rawInput is required.");
    }

    nextSession = orchestrator.chooseUserAuthoredAction(
      session,
      pendingTurn,
      params.authoredAction,
    );
  } else if (params.branchId) {
    nextSession = orchestrator.chooseBranch(session, pendingTurn, params.branchId);
  } else {
    throw new Error("Either branchId or authoredAction is required.");
  }

  nextSession = await prepareNextWebSessionState(nextSession);
  await repository.save(nextSession);
  return nextSession;
}

async function prepareNextWebSessionState(session: SessionState): Promise<SessionState> {
  if (session.status === "complete") {
    const summaryGenerator = createSummaryGenerator();
    return {
      ...session,
      pendingTurn: undefined,
      summary: await summaryGenerator.generate(session),
    };
  }

  const orchestrator = createTurnOrchestrator();
  const nextTurn = await orchestrator.generateTurn(session);
  return {
    ...session,
    pendingTurn: nextTurn,
  };
}
