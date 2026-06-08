import { NextResponse } from "next/server";

import { getWebAblationReport } from "../../../../../src/interfaces/web/session-service";

export async function GET(
  _request: Request,
  context: { params: Promise<{ id: string }> },
) {
  try {
    const { id } = await context.params;
    const report = await getWebAblationReport(id);

    if (!report) {
      return NextResponse.json(
        { error: `Session "${id}" was not found.` },
        { status: 404 },
      );
    }

    return NextResponse.json(report);
  } catch (error) {
    return NextResponse.json(
      {
        error:
          error instanceof Error
            ? error.message
            : "生成消融报告失败。",
      },
      { status: 500 },
    );
  }
}
