import { NextResponse } from "next/server";

import { chooseWebTurnAction } from "../../../../src/interfaces/web/session-service";

function normalizeRiskProfile(riskProfile: unknown) {
  if (
    riskProfile === "low" ||
    riskProfile === "medium" ||
    riskProfile === "high"
  ) {
    return riskProfile;
  }

  return undefined;
}

export async function POST(request: Request) {
  try {
    const body = (await request.json()) as {
      sessionId?: string;
      branchId?: string;
      authoredAction?: {
        rawInput?: string;
        riskProfile?: string;
        timeHorizon?: string;
        anchorBranchId?: string;
      };
    };

    if (!body.sessionId) {
      return NextResponse.json(
        { error: "sessionId 是必填项。" },
        { status: 400 },
      );
    }

    if (!body.branchId && !body.authoredAction?.rawInput?.trim()) {
      return NextResponse.json(
        { error: "branchId 或 authoredAction.rawInput 是必填项。" },
        { status: 400 },
      );
    }

    const session = await chooseWebTurnAction({
      sessionId: body.sessionId,
      branchId: body.branchId,
      authoredAction: body.authoredAction?.rawInput?.trim()
        ? {
            rawInput: body.authoredAction.rawInput.trim(),
            riskProfile: normalizeRiskProfile(body.authoredAction.riskProfile),
            timeHorizon: body.authoredAction.timeHorizon?.trim() || undefined,
            anchorBranchId: body.authoredAction.anchorBranchId?.trim() || undefined,
          }
        : undefined,
    });

    return NextResponse.json(session);
  } catch (error) {
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "选择分支失败。" },
      { status: 500 },
    );
  }
}
