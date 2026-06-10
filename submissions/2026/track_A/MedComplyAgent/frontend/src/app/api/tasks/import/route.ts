function backendBaseUrl(): string {
  return process.env.BACKEND_BASE_URL ?? "http://127.0.0.1:8000";
}

export async function POST(request: Request): Promise<Response> {
  const formData = await request.formData();
  const response = await fetch(`${backendBaseUrl()}/api/tasks/import`, {
    method: "POST",
    body: formData,
    cache: "no-store",
  });

  return new Response(response.body, {
    status: response.status,
    headers: {
      "Content-Type": response.headers.get("Content-Type") ?? "application/json",
    },
  });
}
