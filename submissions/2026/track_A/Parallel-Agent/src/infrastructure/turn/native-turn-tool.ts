import type { NativeJsonToolDefinition } from "../llm/anthropic-client";

export function buildRealityTurnTool(): NativeJsonToolDefinition {
  return {
    name: "simulate_reality_turn",
    description:
      "Generate one Parallel Agent decision turn, including branches, world deltas, stakeholder communities, and causal influence events.",
    parameters: {
      type: "object",
      properties: {
        turnNumber: { type: "number" },
        branches: {
          type: "array",
          items: {
            type: "object",
            properties: {
              id: { type: "string" },
              title: { type: "string" },
              summary: { type: "string" },
              consequence: { type: "string" },
              score: { type: "number" },
              timeHorizon: { type: "string" },
              riskProfile: { type: "string", enum: ["low", "medium", "high"] },
              keyUncertainty: { type: "string" },
            },
            required: [
              "id",
              "title",
              "summary",
              "consequence",
              "score",
              "timeHorizon",
              "riskProfile",
              "keyUncertainty",
            ],
          },
        },
        branchWorldDeltas: {
          type: "array",
          items: {
            type: "object",
            properties: {
              branchId: { type: "string" },
              activatedConstraints: { type: "array", items: { type: "string" } },
              activatedOpportunities: { type: "array", items: { type: "string" } },
              pressureShift: { type: "string" },
            },
            required: [
              "branchId",
              "activatedConstraints",
              "activatedOpportunities",
              "pressureShift",
            ],
          },
        },
        branchCommunities: {
          type: "array",
          items: {
            type: "object",
            properties: {
              branchId: { type: "string" },
              agents: {
                type: "array",
                items: {
                  type: "object",
                  properties: {
                    role: { type: "string" },
                    stance: {
                      type: "string",
                      enum: ["supportive", "resistant", "neutral", "uncertain"],
                    },
                    motivation: { type: "string" },
                    influence: { type: "number" },
                    reaction: { type: "string" },
                  },
                  required: [
                    "role",
                    "stance",
                    "motivation",
                    "influence",
                    "reaction",
                  ],
                },
              },
              socialDynamics: { type: "string" },
              dominantNarrative: { type: "string" },
            },
            required: [
              "branchId",
              "agents",
              "socialDynamics",
              "dominantNarrative",
            ],
          },
        },
        influenceEvents: {
          type: "array",
          items: {
            type: "object",
            properties: {
              id: { type: "string" },
              turn: { type: "number" },
              branchId: { type: "string" },
              sourceType: {
                type: "string",
                enum: ["individual", "society", "environment"],
              },
              sourceId: { type: "string" },
              targetType: {
                type: "string",
                enum: ["individual", "society", "environment"],
              },
              targetId: { type: "string" },
              dimension: {
                type: "string",
                enum: ["trust", "risk", "behavior", "opportunity", "pressure"],
              },
              direction: {
                type: "string",
                enum: ["increase", "decrease", "redirect"],
              },
              intensity: { type: "number" },
              explanation: { type: "string" },
            },
            required: [
              "id",
              "turn",
              "branchId",
              "sourceType",
              "sourceId",
              "targetType",
              "targetId",
              "dimension",
              "direction",
              "intensity",
              "explanation",
            ],
          },
        },
      },
      required: [
        "turnNumber",
        "branches",
        "branchWorldDeltas",
        "branchCommunities",
        "influenceEvents",
      ],
    },
  };
}
