function backendBaseUrl(): string {
  return process.env.BACKEND_BASE_URL ?? "http://127.0.0.1:8000";
}

export async function GET(
  _request: Request,
  context: { params: Promise<{ taskId: string }> }
): Promise<Response> {
  const { taskId } = await context.params;

  const response = await fetch(`${backendBaseUrl()}/api/tasks/${taskId}/pdf`, {
    cache: "no-store",
  });

  if (!response.ok) {
    let message = "PDF file not found";
    try {
      const body = (await response.json()) as { detail?: string };
      if (typeof body.detail === "string" && body.detail.trim()) {
        message = body.detail;
      }
    } catch {
      // Keep the fallback message.
    }

    return new Response(
      `<!doctype html><html><body style="font-family: sans-serif; padding: 16px; color: #3f3f46;"><p>${message}</p></body></html>`,
      {
        status: response.status,
        headers: {
          "Content-Type": "text/html; charset=utf-8",
        },
      }
    );
  }

  return new Response(response.body, {
    status: response.status,
    headers: {
      "Content-Type": response.headers.get("Content-Type") ?? "application/pdf",
    },
  });
}
