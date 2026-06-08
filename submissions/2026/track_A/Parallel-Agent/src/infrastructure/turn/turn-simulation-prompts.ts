import { getPresetScenarioPack } from "../../domain/preset-scenarios";
import type { TurnGenerationInput } from "../../domain/types";

function serializeList(label: string, values: string[]): string {
  if (values.length === 0) {
    return `${label}: none`;
  }

  return `${label}:\n- ${values.join("\n- ")}`;
}

function outputLanguageInstruction(input: TurnGenerationInput): string {
  if (input.session.language === "en") {
    return "Natural-language output fields must be written in English.";
  }

  return [
    "Natural-language output fields must be written in Simplified Chinese.",
    "Keep JSON keys, ids, and enum values in English exactly as specified.",
    "Chinese fields include titles, summaries, consequences, uncertainties, world deltas, agent motivations, reactions, social dynamics, dominant narratives, and influence explanations.",
  ].join("\n");
}

function serializeRecentPath(input: TurnGenerationInput): string {
  const { session } = input;

  if (session.canonicalPath.length === 0) {
    return "canonical path: none";
  }

  return `canonical path:\n${session.canonicalPath
    .map((step) => `- turn ${step.turn}: ${step.title} -> ${step.consequence}`)
    .join("\n")}`;
}

function serializeQuantumTrace(input: TurnGenerationInput): string {
  const { session } = input;

  if (session.quantumTrace.length === 0) {
    return "quantum trace: none";
  }

  return `quantum trace:\n- ${session.quantumTrace.join("\n- ")}`;
}

function serializeUserGrounding(input: TurnGenerationInput): string {
  const { session } = input;

  if (!session.userProvidedData) {
    return "";
  }

  return `
User-provided grounding:
- source count: ${session.userProvidedData.sources.length}
- fact count: ${session.userProvidedData.factItems.length}
- user intent summary: ${session.userProvidedData.derivedBrief.userIntentSummary ?? "none"}
${serializeList("derived constraints", session.userProvidedData.derivedBrief.keyConstraints)}
${serializeList("derived stakeholders", session.userProvidedData.derivedBrief.keyStakeholders)}
${serializeList("derived active options", session.userProvidedData.derivedBrief.activeOptions)}
${serializeList("derived pressures", session.userProvidedData.derivedBrief.decisionPressures)}
user facts:
- ${session.userProvidedData.factItems
    .slice(0, 8)
    .map((fact) => `[${fact.type}] ${fact.summary}`)
    .join("\n- ") || "none"}
`.trim();
}

function serializeSimulationState(input: TurnGenerationInput): string {
  const { session } = input;
  const state = session.simulationState;

  if (!state) {
    return "Simulation state: not initialized";
  }

  const individual = state.individual;
  const skillSummary = Object.entries(individual.skills)
    .map(([name, value]) => `${name}=${formatMetric(value)}`)
    .join(", ");
  const environmentSummary = Object.entries(state.environmentMetrics)
    .map(([name, value]) => `${name}=${formatMetric(value)}`)
    .join(", ");
  const stakeholderSummary =
    state.stakeholders
      .slice(0, 6)
      .map(
        (stakeholder) =>
          `${stakeholder.role} [${stakeholder.stance}] trust=${formatMetric(stakeholder.trust)} resistance=${formatMetric(stakeholder.resistance)} influence=${formatMetric(stakeholder.influence)} goal=${stakeholder.currentGoal}`,
      )
      .join("\n- ") || "none";

  return `
Simulation state:
- scope: ${state.scope}
- updated at turn: ${state.updatedAtTurn}
- individual: confidence=${formatMetric(individual.confidence)}, reputation=${formatMetric(individual.reputation)}, trust=${formatMetric(individual.trust)}, financialStability=${formatMetric(individual.financialStability)}, stress=${formatMetric(individual.stress)}, riskTolerance=${formatMetric(individual.riskTolerance)}
- skills: ${skillSummary || "none"}
- identity: ${individual.identity.join(", ") || "none"}
- environment: ${environmentSummary || "none"}
stakeholders:
- ${stakeholderSummary}
`.trim();
}

function serializePresetGrounding(input: TurnGenerationInput): string {
  const { session } = input;
  const presetScenario = getPresetScenarioPack(session.presetScenarioId);

  if (!presetScenario) {
    return "";
  }

  return `
Preset scenario:
- id: ${presetScenario.scenarioId}
- title: ${presetScenario.title}
- summary: ${presetScenario.summary}
${serializeList("world facts", presetScenario.worldFacts)}
${serializeList("constraints", presetScenario.constraints)}
${serializeList("opportunities", presetScenario.opportunities)}
${serializeList("social tensions", presetScenario.socialTensions)}
role cast:
- ${presetScenario.roleCast
    .map(
      (role) =>
        `${role.role} [${role.baselineStance}] - ${role.relationship}; motivation: ${role.motivation}; influence: ${role.influence}`,
    )
    .join("\n- ")}
User context:
- goal: ${session.userContextPack?.userGoal ?? presetScenario.starterUserContext.userGoal}
- current position: ${session.userContextPack?.currentPosition ?? presetScenario.starterUserContext.currentPosition}
- risk preference: ${session.userContextPack?.riskPreference ?? presetScenario.starterUserContext.riskPreference}
- time horizon: ${session.userContextPack?.timeHorizon ?? presetScenario.starterUserContext.timeHorizon}
${serializeList("key stakeholders", session.userContextPack?.keyStakeholders ?? presetScenario.starterUserContext.keyStakeholders)}
${serializeList("success criteria", session.userContextPack?.successCriteria ?? presetScenario.starterUserContext.successCriteria)}
`.trim();
}

export function buildTurnSimulationPrompt(input: TurnGenerationInput): string {
  const { session, worldContext } = input;
  const latestAuthoredAction = session.userAuthoredActions.at(-1);

  return `
You are Gemma 4 powering Parallel Agent's Reality Engine.

Simulate one decision turn as structured data. Return only valid JSON.
Do not include Markdown, code fences, commentary, or extra top-level keys.
${outputLanguageInstruction(input)}

Session:
- dilemma: ${session.dilemma}
- output language: ${session.language ?? "zh-CN"}
- domain: ${session.domain}
- theme: ${session.theme}
- next turn number: ${session.turn + 1}
- max turns: ${session.maxTurns}

${serializeRecentPath(input)}

${serializeQuantumTrace(input)}

User persona:
- risk tolerance: ${session.userPersona.riskTolerance}
- emotional state: ${session.userPersona.emotionalState}
- primary value: ${session.userPersona.primaryValue}
- recent wins: ${session.userPersona.recentWins.join(", ") || "none"}
- open wounds: ${session.userPersona.openWounds.join(", ") || "none"}

${serializeSimulationState(input)}

${
  latestAuthoredAction
    ? `Recent user-authored action:
- title: ${latestAuthoredAction.title}
- raw input: ${latestAuthoredAction.rawInput}
- risk profile: ${latestAuthoredAction.riskProfile}
- consequence: ${latestAuthoredAction.consequence}`
    : "Recent user-authored action: none"
}

World context:
- setting: ${worldContext.setting}
- external conditions: ${worldContext.externalConditions}
- current world pressure: ${worldContext.currentWorldPressure}
${serializeList("world constraints", worldContext.constraints)}
${serializeList("world opportunities", worldContext.opportunities)}
${serializeList("stable rules", worldContext.stableRules)}

${serializePresetGrounding(input)}

${serializeUserGrounding(input)}

Output requirements:
1. Generate exactly 3 branches.
2. Branches must be meaningfully different in risk, direction, and consequence.
3. Return one branchWorldDelta per branch.
4. Return one branchCommunity per branch, with exactly 3 agents per community.
5. Return at least 2 influenceEvents per branch:
   - one individual -> society or environment event
   - one society or environment -> individual event
6. influenceEvents are the causal bridge for macro/micro analysis. Keep them concrete.
7. Scores must be decimals between 0 and 1. They do not need to sum to 1; Parallel Agent will normalize.
8. Use only these enum values:
   - riskProfile: low | medium | high
   - stance: supportive | resistant | neutral | uncertain
   - sourceType/targetType: individual | society | environment
   - dimension: trust | risk | behavior | opportunity | pressure
   - direction: increase | decrease | redirect

Return JSON with this exact top-level shape:
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
  ],
  "branchCommunities": [
    {
      "branchId": "b1",
      "agents": [
        {
          "role": "string",
          "stance": "supportive | resistant | neutral | uncertain",
          "motivation": "string",
          "influence": 0.7,
          "reaction": "string"
        }
      ],
      "socialDynamics": "string",
      "dominantNarrative": "string"
    }
  ],
  "influenceEvents": [
    {
      "id": "ie-1-b1-individual-to-society",
      "turn": ${session.turn + 1},
      "branchId": "b1",
      "sourceType": "individual",
      "sourceId": "observer",
      "targetType": "society",
      "targetId": "manager",
      "dimension": "trust",
      "direction": "increase",
      "intensity": 0.6,
      "explanation": "string"
    }
  ]
}
`.trim();
}

function formatMetric(value: number): string {
  return value.toFixed(2);
}
