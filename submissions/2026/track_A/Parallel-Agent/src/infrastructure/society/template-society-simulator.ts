import type { SocietySimulator } from "../../application/ports";
import { getPresetScenarioPack } from "../../domain/preset-scenarios";
import { branchCommunitiesSchema } from "../../domain/schemas";
import type {
  Branch,
  BranchCommunity,
  SocietySimulationInput,
} from "../../domain/types";

function communityForBranch(
  branch: Branch,
  input: SocietySimulationInput,
): BranchCommunity {
  const presetScenario = getPresetScenarioPack(input.session.presetScenarioId);

  if (presetScenario) {
    const agents = presetScenario.roleCast.slice(0, 3).map((role) => ({
      role: role.role,
      stance:
        branch.riskProfile === "high"
          ? role.baselineStance === "resistant"
            ? "resistant"
            : "uncertain"
          : branch.riskProfile === "low"
            ? role.baselineStance === "uncertain"
              ? "supportive"
              : role.baselineStance
            : role.baselineStance,
      motivation: role.motivation,
      influence: role.influence,
      reaction: buildScenarioReaction(role.role, branch, input),
    }));

    return {
      branchId: branch.id,
      agents,
      socialDynamics:
        presetScenario.socialTensions[1] ??
        "Observers are trying to decide whether this move is adaptation, theater, or overcorrection.",
      dominantNarrative:
        branch.riskProfile === "high"
          ? "People around you read this as a high-visibility attempt to redefine your role before the field does it for you."
          : branch.riskProfile === "low"
            ? "People around you read this as a cautious attempt to stay credible while the field shifts."
            : "People around you read this as a measured attempt to become AI-native without losing trust.",
    };
  }

  const agents =
    branch.riskProfile === "high"
      ? [
          {
            role: "Hiring Manager",
            stance: "supportive" as const,
            motivation: "Needs visible commitment from you.",
            influence: 0.9,
            reaction: `Pushes for speed and ownership inside ${input.worldContext.setting.toLowerCase()}.`,
          },
          {
            role: "Family",
            stance: "uncertain" as const,
            motivation: "Wants upside without chaos.",
            influence: 0.7,
            reaction:
              "Supports the move but worries about sustainability and emotional spillover.",
          },
          {
            role: "Peer Mentor",
            stance: "neutral" as const,
            motivation: "Wants the choice to be legible and strategic.",
            influence: 0.5,
            reaction: `Encourages clarity about what success must look like under ${input.worldContext.currentWorldPressure.toLowerCase()}.`,
          },
        ]
      : branch.riskProfile === "low"
        ? [
            {
              role: "Current Manager",
              stance: "supportive" as const,
              motivation: "Values continuity and trust.",
              influence: 0.8,
              reaction: "Rewards steadiness if it still signals ambition and growth.",
            },
            {
              role: "External Recruiter",
              stance: "resistant" as const,
              motivation: "Wants you to keep the market option alive.",
              influence: 0.4,
              reaction: "Frames caution as missed leverage and fading momentum.",
            },
            {
              role: "Close Friend",
              stance: "supportive" as const,
              motivation: "Wants you to avoid regret.",
              influence: 0.6,
              reaction: "Pushes you to preserve optionality even while staying grounded.",
            },
          ]
        : [
            {
              role: "Current Manager",
              stance: "uncertain" as const,
              motivation: "Needs predictability without losing your contribution.",
              influence: 0.7,
              reaction: "Accepts a phased path but watches for signs of split commitment.",
            },
            {
              role: "Startup Founder",
              stance: "supportive" as const,
              motivation: "Wants evidence you are serious without forcing a full leap yet.",
              influence: 0.8,
              reaction: "Welcomes momentum if the arrangement still moves fast enough.",
            },
            {
              role: "Partner or Family",
              stance: "supportive" as const,
              motivation: "Reduce downside while keeping growth alive.",
              influence: 0.75,
              reaction: "Sees the compromise as smart, but worries complexity will linger.",
            },
          ];

  return {
    branchId: branch.id,
    agents,
    socialDynamics:
      branch.riskProfile === "high"
        ? "Support comes with pressure for visible commitment and rapid execution."
        : branch.riskProfile === "low"
          ? "Stability creates trust, but some observers worry it may narrow the field."
          : "Mixed loyalties create a balancing act between safety and momentum.",
    dominantNarrative:
      branch.riskProfile === "high"
        ? "People around you read this as a momentum-first bet."
        : branch.riskProfile === "low"
          ? "People around you read this as a durability-first move."
          : "People around you read this as a bridge strategy that preserves optionality.",
  };
}

function buildScenarioReaction(
  role: string,
  branch: Branch,
  input: SocietySimulationInput,
): string {
  const pressure = input.worldContext.currentWorldPressure.toLowerCase();

  if (role.toLowerCase().includes("manager")) {
    return branch.riskProfile === "high"
      ? `Pushes for proof that the bold repositioning will improve outcomes under ${pressure}.`
      : `Wants the move to stay legible, credible, and operational under ${pressure}.`;
  }

  if (role.toLowerCase().includes("peer")) {
    return branch.riskProfile === "high"
      ? "Reads the move as status-signaling unless the execution quality becomes obvious fast."
      : "Watches closely to see whether this is practical adaptation or just low-risk self-protection.";
  }

  if (role.toLowerCase().includes("ai-forward")) {
    return "Supports experimentation, but expects visible leverage rather than abstract enthusiasm.";
  }

  return "Supports growth, but worries about sustainability, identity drift, and second-order stress.";
}

export class TemplateSocietySimulator implements SocietySimulator {
  async simulate(input: SocietySimulationInput): Promise<BranchCommunity[]> {
    return branchCommunitiesSchema.parse(
      input.branches.map((branch) => communityForBranch(branch, input)),
    );
  }
}
