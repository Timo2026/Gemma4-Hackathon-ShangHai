import { getPresetScenarioPack } from "../../domain/preset-scenarios";
import type { WorldModelProvider } from "../../application/ports";
import type { SessionState, WorldContext } from "../../domain/types";

function inferCareerConstraints(dilemma: string): string[] {
  const text = dilemma.toLowerCase();
  const constraints = ["Career moves take time to compound."];

  if (text.includes("startup")) constraints.push("Early-stage companies amplify uncertainty.");
  if (text.includes("city") || text.includes("relocat")) {
    constraints.push("Relocation creates social and logistical switching costs.");
  }
  if (text.includes("offer")) constraints.push("Negotiation windows are short and reputationally sensitive.");

  return constraints;
}

function inferCareerOpportunities(dilemma: string): string[] {
  const text = dilemma.toLowerCase();
  const opportunities = ["A single visible decision can change future positioning."];

  if (text.includes("startup")) opportunities.push("Smaller teams can create faster learning loops.");
  if (text.includes("manager") || text.includes("promotion")) {
    opportunities.push("Internal reputation can open compounding leadership opportunities.");
  }
  if (text.includes("offer")) opportunities.push("Competing paths can improve leverage and clarity.");

  return opportunities;
}

export class NarrativeWorldModelProvider implements WorldModelProvider {
  async getContext(session: SessionState): Promise<WorldContext> {
    const constraints = inferCareerConstraints(session.dilemma);
    const opportunities = inferCareerOpportunities(session.dilemma);
    const latestAuthoredAction = session.userAuthoredActions.at(-1);
    const presetScenario = getPresetScenarioPack(session.presetScenarioId);

    if (presetScenario) {
      constraints.push(...presetScenario.constraints);
      opportunities.push(...presetScenario.opportunities);
    }

    if (latestAuthoredAction?.turn === session.turn) {
      constraints.push(
        "A user-authored move creates interpretation risk until others understand what it means in practice.",
      );
      opportunities.push(
        "A user-authored move can expose higher-agency paths than the default branch menu revealed.",
      );
    }

    const setting =
      latestAuthoredAction?.turn === session.turn
        ? `A continuing career journey reshaped by a self-authored move: ${latestAuthoredAction.title.toLowerCase()}.`
        : presetScenario
          ? `${presetScenario.summary} ${presetScenario.worldFacts[0]}`
        : session.canonicalPath.length === 0
        ? "A current-career decision point with limited information and real reputational stakes."
        : `A continuing career journey shaped by ${session.canonicalPath.at(-1)?.title.toLowerCase()}.`;

    const externalConditions =
      latestAuthoredAction?.turn === session.turn
        ? "The environment reacts not only to the decision itself, but to the fact that you authored your own path."
        : presetScenario
          ? presetScenario.seedNarratives[0] ??
            "The surrounding field is changing fast enough that static roles are becoming unstable."
        : session.userPersona.riskTolerance === "high"
        ? "The market rewards bold moves but punishes sloppy execution."
        : "The market favors deliberate positioning and credible follow-through.";

    return {
      domain: session.domain,
      setting,
      externalConditions,
      constraints,
      opportunities,
      stableRules: [
        "Trust changes slower than excitement.",
        "Career upside is usually paired with visible trade-offs.",
        "Social support affects whether hard choices remain sustainable.",
        "Self-authored moves increase agency, but also increase legibility pressure.",
        ...(presetScenario?.worldFacts ?? []).slice(0, 2),
      ],
      currentWorldPressure:
        latestAuthoredAction?.turn === session.turn
          ? `The world is now testing whether ${latestAuthoredAction.title.toLowerCase()} can become legible and sustainable.`
          : presetScenario
            ? presetScenario.socialTensions[0] ??
              "The next move will signal whether you are adapting early or reacting late."
          : session.quantumTrace.at(-1) ??
            "The next move will signal what kind of career story is becoming real.",
    };
  }
}
