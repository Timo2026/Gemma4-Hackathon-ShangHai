import { randomUUID } from "node:crypto";

import { getPresetScenarioPack } from "./preset-scenarios";
import { createInitialSimulationState } from "./simulation-state";
import { normalizeUserProvidedDataInput } from "./user-provided-data";
import type {
  Domain,
  OutputLanguage,
  SessionState,
  Theme,
  UserContextPack,
  UserContextPackInput,
  UserPersona,
  UserProvidedDataInput,
} from "./types";

const defaultPersona: UserPersona = {
  riskTolerance: "medium",
  emotionalState: "curious",
  primaryValue: "clarity",
  recentWins: [],
  openWounds: [],
};

export function createSession(params: {
  dilemma?: string;
  theme?: Theme;
  domain?: Domain;
  maxTurns?: number;
  presetScenarioId?: SessionState["presetScenarioId"];
  language?: OutputLanguage;
  userContextPack?: UserContextPackInput;
  userProvidedData?: UserProvidedDataInput;
}): SessionState {
  const presetScenario = getPresetScenarioPack(params.presetScenarioId);
  const dilemma = params.dilemma?.trim() || presetScenario?.baseDilemma;

  if (!dilemma) {
    throw new Error("A dilemma or preset scenario is required to create a session.");
  }

  const userPersona = presetScenario
    ? {
        ...defaultPersona,
        riskTolerance: presetScenario.starterUserContext.riskPreference,
        emotionalState: "watchful",
        primaryValue: "adaptability",
      }
    : { ...defaultPersona };
  const userContextPack = mergeUserContextPack(
    presetScenario?.starterUserContext,
    params.userContextPack,
  );

  const initialSimulationState = createInitialSimulationState({
    userPersona,
    userContextPack,
    presetScenario,
    turn: 0,
  });

  return {
    sessionId: randomUUID(),
    dilemma,
    language: params.language ?? "zh-CN",
    domain: params.domain ?? presetScenario?.domain ?? "career",
    theme: params.theme ?? presetScenario?.theme ?? "sci-fi",
    presetScenarioId: params.presetScenarioId,
    turn: 0,
    maxTurns: params.maxTurns ?? 5,
    status: "active",
    canonicalPath: [],
    quantumTrace: [],
    shadowTimelines: [],
    userContextPack,
    userProvidedData: normalizeUserProvidedDataInput(params.userProvidedData),
    userAuthoredActions: [],
    toolCalls: [],
    influenceEvents: [],
    initialSimulationState,
    simulationState: initialSimulationState,
    groundingLog: [],
    userPersona,
  };
}

function mergeUserContextPack(
  basePack: UserContextPack | undefined,
  overridePack: UserContextPackInput | undefined,
): UserContextPack | undefined {
  if (!basePack && !overridePack) {
    return undefined;
  }

  const mergedBase: UserContextPack = basePack ?? {
    userGoal: "Clarify the next move.",
    currentPosition: "A person navigating a changing career situation.",
    availableOptions: [],
    riskPreference: "medium",
    timeHorizon: "3-6 months",
    personalConstraints: [],
    keyStakeholders: [],
    successCriteria: [],
  };

  return {
    userGoal: overridePack?.userGoal?.trim() || mergedBase.userGoal,
    currentPosition:
      overridePack?.currentPosition?.trim() || mergedBase.currentPosition,
    availableOptions:
      overridePack?.availableOptions?.filter(Boolean) ?? mergedBase.availableOptions,
    riskPreference: overridePack?.riskPreference ?? mergedBase.riskPreference,
    timeHorizon: overridePack?.timeHorizon?.trim() || mergedBase.timeHorizon,
    personalConstraints:
      overridePack?.personalConstraints?.filter(Boolean) ??
      mergedBase.personalConstraints,
    keyStakeholders:
      overridePack?.keyStakeholders?.filter(Boolean) ?? mergedBase.keyStakeholders,
    successCriteria:
      overridePack?.successCriteria?.filter(Boolean) ?? mergedBase.successCriteria,
  };
}

export function assertSessionIsActive(session: SessionState): void {
  if (session.status !== "active") {
    throw new Error(`Session ${session.sessionId} is not active.`);
  }
}

export function nextTurnNumber(session: SessionState): number {
  return session.turn + 1;
}

export function markSessionAbandoned(session: SessionState): SessionState {
  return {
    ...session,
    status: "abandoned",
  };
}

export function markSessionComplete(session: SessionState): SessionState {
  return {
    ...session,
    status: "complete",
  };
}
