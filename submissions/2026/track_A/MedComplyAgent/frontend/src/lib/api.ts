import type {
  ConfirmRequest,
  ConfirmResponse,
  ExtractResponse,
  TaskDetail,
  TaskSummary,
} from "@/lib/types";

async function requestJson<T>(input: string, init?: RequestInit): Promise<T> {
  const response = await fetch(input, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
    cache: "no-store",
  });

  if (!response.ok) {
    let detail = `Request failed with status ${response.status}`;
    try {
      const body = (await response.json()) as { detail?: string };
      if (typeof body.detail === "string") {
        detail = body.detail;
      }
    } catch {
      // keep fallback detail
    }
    throw new Error(detail);
  }

  return (await response.json()) as T;
}

export function listTasks(): Promise<TaskSummary[]> {
  return requestJson<TaskSummary[]>("/api/tasks");
}

export async function importTaskPdf(formData: FormData): Promise<TaskSummary> {
  const response = await fetch("/api/tasks/import", {
    method: "POST",
    body: formData,
    cache: "no-store",
  });

  if (!response.ok) {
    let detail = `Request failed with status ${response.status}`;
    try {
      const body = (await response.json()) as { detail?: string };
      if (typeof body.detail === "string") {
        detail = body.detail;
      }
    } catch {
      // keep fallback detail
    }
    throw new Error(detail);
  }

  return (await response.json()) as TaskSummary;
}

export function getTask(taskId: number): Promise<TaskDetail> {
  return requestJson<TaskDetail>(`/api/tasks/${taskId}`);
}

export function extractTask(taskId: number): Promise<ExtractResponse> {
  return requestJson<ExtractResponse>(`/api/tasks/${taskId}/extract`, {
    method: "POST",
  });
}

export function confirmTask(taskId: number, payload: ConfirmRequest): Promise<ConfirmResponse> {
  return requestJson<ConfirmResponse>(`/api/tasks/${taskId}/confirm`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
