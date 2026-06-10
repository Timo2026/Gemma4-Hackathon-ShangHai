import type { BranchGenerator } from "../../application/ports";
import { turnDraftSchema } from "../../domain/schemas";
import type {
  Branch,
  BranchWorldDelta,
  RiskProfile,
  TurnDraft,
  TurnGenerationInput,
} from "../../domain/types";

function buildBranch(
  id: string,
  title: string,
  summary: string,
  consequence: string,
  score: number,
  timeHorizon: string,
  riskProfile: RiskProfile,
  keyUncertainty: string,
): Branch {
  return {
    id,
    title,
    summary,
    consequence,
    score,
    timeHorizon,
    riskProfile,
    keyUncertainty,
  };
}

function branchSetForTurn(input: TurnGenerationInput): Branch[] {
  const { session, worldContext } = input;
  const previousChoice = session.canonicalPath.at(-1)?.title;

  if (session.turn === 0) {
    return [
      buildBranch(
        "b1",
        "Take The Leap",
        `You accept the more accelerated path and enter a faster cycle of learning. ${worldContext.externalConditions}`,
        "fast growth with unstable rhythm",
        0.42,
        "6-12 months",
        "high",
        "Whether momentum turns into durable support.",
      ),
      buildBranch(
        "b2",
        "Stay Anchored",
        "You keep the stable path, deepen trust where you are, and try to compound credibility before making a bigger move.",
        "steady growth with slower change",
        0.34,
        "12-18 months",
        "low",
        "Whether patience becomes stagnation.",
      ),
      buildBranch(
        "b3",
        "Negotiate A Bridge",
        "You try to create a hybrid move that keeps optionality alive, buying time while testing whether the opportunity is truly real.",
        "flexibility with mixed trust",
        0.24,
        "3-6 months",
        "medium",
        "Whether both sides see the bridge as commitment or hesitation.",
      ),
    ];
  }

  const traceTail = session.quantumTrace.at(-1) ?? "Your last move shifted the field.";

  return [
    buildBranch(
      "b1",
      "Double Down",
      `Because you previously chose ${previousChoice?.toLowerCase() ?? "movement"}, the world now offers a more committed version of that path. ${traceTail}`,
      "greater upside with sharper exposure",
      0.38,
      "6-9 months",
      "high",
      "Whether the stronger commitment outruns your support system.",
    ),
    buildBranch(
      "b2",
      "Create A Retreat",
      "You try to preserve what you gained while reducing fragility, renegotiating pace, expectations, or scope before the pressure compounds.",
      "reduced risk with possible loss of momentum",
      0.32,
      "2-4 months",
      "medium",
      "Whether caution is read as maturity or hesitation.",
    ),
    buildBranch(
      "b3",
      "Change The Frame",
      "A third path appears: instead of pushing harder or retreating, you reposition the decision so a different kind of opportunity becomes visible.",
      "new optionality with identity shift",
      0.3,
      "9-12 months",
      "medium",
      "Whether the new frame creates real leverage or just delay.",
    ),
  ];
}

function worldDeltaForBranch(branch: Branch): BranchWorldDelta {
  return {
    branchId: branch.id,
    activatedConstraints:
      branch.riskProfile === "high"
        ? ["Execution pressure rises quickly."]
        : ["Slower paths can be mistaken for passivity."],
    activatedOpportunities:
      branch.riskProfile === "high"
        ? ["Visibility and accelerated learning increase."]
        : ["Trust and optionality can deepen over time."],
    pressureShift:
      branch.riskProfile === "high"
        ? "The world now expects you to justify boldness with execution."
        : "The world now tests whether patience still carries ambition.",
  };
}

export class MockBranchGenerator implements BranchGenerator {
  async generate(input: TurnGenerationInput): Promise<TurnDraft> {
    const branches = branchSetForTurn(input);
    const branchWorldDeltas = branches.map(worldDeltaForBranch);

    return turnDraftSchema.parse({
      turnNumber: input.session.turn + 1,
      branches,
      branchWorldDeltas,
    });
  }
}
