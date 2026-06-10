import type { SummaryGenerator } from "../../application/ports";
import type { SessionState, SessionSummary } from "../../domain/types";

export class MockSummaryGenerator implements SummaryGenerator {
  async generate(session: SessionState): Promise<SessionSummary> {
    const finalStep = session.canonicalPath.at(-1);
    const shadowByTurn = session.shadowTimelines
      .map((branches, index) => {
        const branch = branches[0];
        return branch
          ? `turn ${index + 1}: ${branch.title} could have led to ${branch.consequence}`
          : undefined;
      })
      .filter(Boolean)
      .join("; ");

    return {
      narrative: `You moved through ${session.turn} turns of uncertainty and gradually clarified what kind of path you were willing to own. The journey ended at ${
        finalStep?.title ?? "an unresolved crossroads"
      }, where the trade-off of ${finalStep?.consequence ?? "change"} became concrete instead of abstract.`,
      decisionArc: [
        `The path repeatedly tested ${session.userPersona.primaryValue}.`,
        `Risk tolerance settled at ${session.userPersona.riskTolerance}.`,
        `The journey left a residue of ${session.userPersona.emotionalState}.`,
      ],
      alternateHint:
        shadowByTurn
          ? `Roads not taken remained visible: ${shadowByTurn}.`
          : undefined,
    };
  }
}
