import type {
  Branch,
  BranchCommunity,
  BranchWorldDelta,
  RiskProfile,
  SessionState,
  UserPersona,
} from "./types";

function personaValueFromRisk(riskProfile: RiskProfile): string {
  if (riskProfile === "high") return "ambition";
  if (riskProfile === "low") return "stability";
  return "optionality";
}

function emotionalStateFromRisk(riskProfile: RiskProfile): string {
  if (riskProfile === "high") return "charged";
  if (riskProfile === "low") return "steady";
  return "alert";
}

function buildTraceEntries(
  selectedBranch: Branch,
  branchWorldDelta?: BranchWorldDelta,
  branchCommunity?: BranchCommunity,
): string[] {
  const entries: string[] = [
    `Chose ${selectedBranch.title.toLowerCase()} and moved toward ${selectedBranch.consequence.toLowerCase()}.`,
    `Accepted a ${selectedBranch.riskProfile}-risk path with a ${selectedBranch.timeHorizon.toLowerCase()} horizon.`,
  ];

  if (branchWorldDelta?.pressureShift) {
    entries.push(branchWorldDelta.pressureShift);
  }

  if (branchCommunity?.dominantNarrative) {
    entries.push(branchCommunity.dominantNarrative);
  }

  return entries;
}

function updatePersona(
  previousPersona: UserPersona,
  selectedBranch: Branch,
): UserPersona {
  const nextValue = personaValueFromRisk(selectedBranch.riskProfile);
  const nextEmotion = emotionalStateFromRisk(selectedBranch.riskProfile);

  const recentWins = [...previousPersona.recentWins, selectedBranch.title].slice(-3);
  const openWounds =
    selectedBranch.riskProfile === "high"
      ? [...previousPersona.openWounds, selectedBranch.keyUncertainty].slice(-3)
      : previousPersona.openWounds.slice(-3);

  return {
    riskTolerance: selectedBranch.riskProfile,
    emotionalState: nextEmotion,
    primaryValue: nextValue,
    recentWins,
    openWounds,
  };
}

export function encodeEntanglement(params: {
  session: SessionState;
  selectedBranch: Branch;
  branchWorldDelta?: BranchWorldDelta;
  branchCommunity?: BranchCommunity;
}): SessionState {
  const newEntries = buildTraceEntries(
    params.selectedBranch,
    params.branchWorldDelta,
    params.branchCommunity,
  );

  const quantumTrace = [...params.session.quantumTrace, ...newEntries].slice(-5);

  return {
    ...params.session,
    quantumTrace,
    userPersona: updatePersona(params.session.userPersona, params.selectedBranch),
  };
}
