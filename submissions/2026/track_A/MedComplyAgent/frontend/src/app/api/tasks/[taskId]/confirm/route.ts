function backendBaseUrl(): string {
  return process.env.BACKEND_BASE_URL ?? "http://127.0.0.1:8000";
}

export async function POST(
  request: Request,
  context: { params: Promise<{ taskId: string }> }
): Promise<Response> {
  const { taskId } = await context.params;
  const body = await request.text();

  const response = await fetch(`${backendBaseUrl()}/api/tasks/${taskId}/confirm`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body,
    cache: "no-store",
  });

  return new Response(response.body, {
    status: response.status,
    headers: {
      "Content-Type": response.headers.get("Content-Type") ?? "application/json",
    },
  });
}
