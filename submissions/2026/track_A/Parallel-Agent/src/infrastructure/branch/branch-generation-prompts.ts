import { getPresetScenarioPack } from "../../domain/preset-scenarios";
import type { TurnGenerationInput } from "../../domain/types";

function serializeList(label: string, values: string[]): string {
  if (values.length === 0) {
    return `${label}: none`;
  }

  return `${label}:\n- ${values.join("\n- ")}`;
}

function serializeRoleCast(
  roles: Array<{
    role: string;
    relationship: string;
    baselineStance: string;
    motivation: string;
  }>,
): string {
  if (roles.length === 0) {
    return "role cast: none";
  }

  return `role cast:\n- ${roles
    .map(
      (role) =>
        `${role.role} [${role.baselineStance}] - ${role.relationship}; motivation: ${role.motivation}`,
    )
    .join("\n- ")}`;
}

function serializeUserProvidedFacts(
  facts: Array<{
    type: string;
    summary: string;
  }>,
): string {
  if (facts.length === 0) {
    return "user-provided facts: none";
  }

  return `user-provided facts:\n- ${facts
    .map((fact) => `[${fact.type}] ${fact.summary}`)
    .join("\n- ")}`;
}

function serializeRecentAuthoredAction(
  action:
    | {
        title: string;
        rawInput: string;
        riskProfile: string;
        consequence: string;
      }
    | undefined,
): string {
  if (!action) {
    return "recent user-authored action: none";
  }

  return `recent user-authored action:
- title: ${action.title}
- raw input: ${action.rawInput}
- risk profile: ${action.riskProfile}
- consequence: ${action.consequence}`;
}

export function buildClaudeBranchGenerationPrompt(
  input: TurnGenerationInput,
): string {
  const { session, worldContext } = input;
  const presetScenario = getPresetScenarioPack(session.presetScenarioId);
  const canonicalPath =
    session.canonicalPath.length === 0
      ? "No prior choices yet."
      : session.canonicalPath
          .map(
            (step) =>
              `Turn ${step.turn}: ${step.title} -> ${step.consequence}`,
          )
          .join("\n");

  const quantumTrace =
    session.quantumTrace.length === 0
      ? "No quantum trace yet."
      : session.quantumTrace.map((entry) => `- ${entry}`).join("\n");
  const latestAuthoredAction = session.userAuthoredActions.at(-1);

  return `
You are Parallel Agent, a quantum-inspired decision engine.

Your job is to generate the next turn of a branching decision session.
Return only valid JSON. Do not add commentary before or after the JSON.
Do not include Markdown, code fences, or explanatory text.

Session:
- dilemma: ${session.dilemma}
- domain: ${session.domain}
- theme: ${session.theme}
- next turn number: ${session.turn + 1}
- max turns: ${session.maxTurns}

Canonical path so far:
${canonicalPath}

Quantum trace:
${quantumTrace}

${serializeRecentAuthoredAction(latestAuthoredAction)}

User persona:
- risk tolerance: ${session.userPersona.riskTolerance}
- emotional state: ${session.userPersona.emotionalState}
- primary value: ${session.userPersona.primaryValue}
- recent wins: ${session.userPersona.recentWins.join(", ") || "none"}
- open wounds: ${session.userPersona.openWounds.join(", ") || "none"}

World context:
- setting: ${worldContext.setting}
- external conditions: ${worldContext.externalConditions}
- current world pressure: ${worldContext.currentWorldPressure}
${serializeList("constraints", worldContext.constraints)}
${serializeList("opportunities", worldContext.opportunities)}
${serializeList("stable rules", worldContext.stableRules)}

${
  session.userProvidedData
    ? `User-provided grounding:
- source count: ${session.userProvidedData.sources.length}
- fact count: ${session.userProvidedData.factItems.length}
- user intent summary: ${session.userProvidedData.derivedBrief.userIntentSummary ?? "none"}
${serializeList("derived key constraints", session.userProvidedData.derivedBrief.keyConstraints)}
${serializeList("derived key stakeholders", session.userProvidedData.derivedBrief.keyStakeholders)}
${serializeList("derived active options", session.userProvidedData.derivedBrief.activeOptions)}
${serializeList("derived decision pressures", session.userProvidedData.derivedBrief.decisionPressures)}
${serializeUserProvidedFacts(
  session.userProvidedData.factItems.slice(0, 8).map((fact) => ({
    type: fact.type,
    summary: fact.summary,
  })),
)}
`
    : ""
}

${
  presetScenario
    ? `Preset scenario:
- id: ${presetScenario.scenarioId}
- title: ${presetScenario.title}
- summary: ${presetScenario.summary}
${serializeList("world facts", presetScenario.worldFacts)}
${serializeList("social tensions", presetScenario.socialTensions)}
${serializeList("seed narratives", presetScenario.seedNarratives)}
${serializeRoleCast(presetScenario.roleCast)}
Grounding user context:
- goal: ${session.userContextPack?.userGoal ?? presetScenario.starterUserContext.userGoal}
- current position: ${session.userContextPack?.currentPosition ?? presetScenario.starterUserContext.currentPosition}
- risk preference: ${session.userContextPack?.riskPreference ?? presetScenario.starterUserContext.riskPreference}
- time horizon: ${session.userContextPack?.timeHorizon ?? presetScenario.starterUserContext.timeHorizon}
${serializeList(
  "available options",
  session.userContextPack?.availableOptions ??
    presetScenario.starterUserContext.availableOptions,
)}
${serializeList(
  "personal constraints",
  session.userContextPack?.personalConstraints ??
    presetScenario.starterUserContext.personalConstraints,
)}
${serializeList(
  "key stakeholders",
  session.userContextPack?.keyStakeholders ??
    presetScenario.starterUserContext.keyStakeholders,
)}
${serializeList(
  "success criteria",
  session.userContextPack?.successCriteria ??
    presetScenario.starterUserContext.successCriteria,
)}
`
    : ""
}

Output requirements:
1. Generate exactly 3 branches.
2. Branches must be meaningfully different in risk, direction, and consequence.
3. Keep titles short and vivid.
4. Keep summaries compact but concrete.
5. Keep consequences short and decision-relevant.
6. Scores must be decimals between 0 and 1.
7. For each branch, provide a world delta.
8. The world deltas should make the next-turn pressure feel causally different.
${
  latestAuthoredAction
    ? "9. These branches must respond to the recent user-authored action, not ignore it. At least one branch should consolidate it, one should redirect it, or one should surface its social/world consequences."
    : ""
}

Return JSON with this exact shape:
{
  "turnNumber": ${session.turn + 1},
  "branches": [
    {
      "id": "b1",
      "title": "string",
      "summary": "string",
      "consequence": "string",
      "score": 0.34,
      "timeHorizon": "string",
      "riskProfile": "low | medium | high",
      "keyUncertainty": "string"
    }
  ],
  "branchWorldDeltas": [
    {
      "branchId": "b1",
      "activatedConstraints": ["string"],
      "activatedOpportunities": ["string"],
      "pressureShift": "string"
    }
  ]
}
`.trim();
}
