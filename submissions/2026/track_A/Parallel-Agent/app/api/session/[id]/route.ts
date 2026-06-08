import { NextResponse } from "next/server";

import { getWebSession } from "../../../../src/interfaces/web/session-service";

export async function GET(
  _request: Request,
  context: { params: Promise<{ id: string }> },
) {
  try {
    const { id } = await context.params;
    const session = await getWebSession(id);

    if (!session) {
      return NextResponse.json(
        { error: `Session "${id}" was not found.` },
        { status: 404 },
      );
    }

    return NextResponse.json(session);
  } catch (error) {
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "加载 session 失败。" },
      { status: 500 },
    );
  }
}
