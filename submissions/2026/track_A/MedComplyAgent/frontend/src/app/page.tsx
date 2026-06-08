"use client";

import Link from "next/link";
import { type FormEvent, useEffect, useMemo, useState } from "react";

import { MockAuthGate, MockLogoutButton } from "@/components/ui/mock-auth-gate";
import { StatusPill } from "@/components/ui/status-pill";
import { useToast } from "@/components/ui/toast-provider";
import { importTaskPdf, listTasks } from "@/lib/api";
import type { TaskSummary } from "@/lib/types";

const PAGE_SIZE = 10;

function statusTone(status: string): "slate" | "blue" | "emerald" {
  if (status === "CONFIRMED") {
    return "emerald";
  }
  if (status === "EXTRACTED") {
    return "blue";
  }
  return "slate";
}

function gapTone(gapStatus: string | null): "emerald" | "rose" | "slate" {
  if (gapStatus === "Closed") {
    return "emerald";
  }
  if (gapStatus === "Open") {
    return "rose";
  }
  return "slate";
}

function inferMeasureFromFilename(filename: string): string {
  const lower = filename.toLowerCase();
  if (lower.includes("cbp")) {
    return "CBP";
  }
  if (lower.includes("bpd")) {
    return "BPD";
  }
  if (lower.includes("gsd")) {
    return "GSD";
  }
  return "";
}

function inferPatientNameFromFilename(filename: string): string {
  const base = filename.replace(/\.pdf$/i, "");
  const tokens = base.split(/[_\-\s]+/).filter(Boolean);
  const stopTokens = new Set(["CBP", "BPD", "GSD", "ED", "IP", "INPATIENT", "OUTPATIENT", "TEL", "TELEHEALTH", "REMOTE", "RPM"]);
  const nameTokens: string[] = [];

  for (const token of tokens) {
    const upper = token.toUpperCase();
    if (stopTokens.has(upper) || /^\d+$/.test(token)) {
      break;
    }
    nameTokens.push(token);
  }

  return nameTokens.join(" ");
}

function MetricCard({
  label,
  value,
  accent,
}: {
  label: string;
  value: string;
  accent: string;
}) {
  return (
    <div className="min-w-[160px] rounded-2xl border border-slate-200 bg-white px-4 py-4 shadow-sm shadow-slate-900/5">
      <div className={`h-1.5 w-12 rounded-full ${accent}`} />
      <p className="mt-3 text-xs font-medium uppercase tracking-[0.04em] text-slate-500">{label}</p>
      <p className="mt-2 text-3xl font-semibold tracking-tight text-slate-900">{value}</p>
    </div>
  );
}

export default function Home() {
  const [tasks, setTasks] = useState<TaskSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [uploadOpen, setUploadOpen] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [measureCodes, setMeasureCodes] = useState("");
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [requestedPage, setRequestedPage] = useState(1);
  const { showToast } = useToast();

  async function loadTasks() {
    try {
      setLoading(true);
      const items = await listTasks();
      setTasks(items);
      setError(null);
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : "Failed to load tasks");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    let cancelled = false;

    async function loadInitialTasks() {
      try {
        setLoading(true);
        const items = await listTasks();
        if (!cancelled) {
          setTasks(items);
          setError(null);
        }
      } catch (loadError) {
        if (!cancelled) {
          setError(loadError instanceof Error ? loadError.message : "Failed to load tasks");
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    void loadInitialTasks();

    return () => {
      cancelled = true;
    };
  }, []);

  const dashboardMetrics = useMemo(() => {
    const openGaps = tasks.filter((task) => task.gap_status !== "Closed").length;
    const awaitingReview = tasks.filter((task) => task.status !== "CONFIRMED").length;
    const confirmed = tasks.filter((task) => task.status === "CONFIRMED").length;
    return {
      total: tasks.length,
      openGaps,
      awaitingReview,
      confirmed,
    };
  }, [tasks]);

  const totalPages = Math.max(1, Math.ceil(tasks.length / PAGE_SIZE));
  const currentPage = Math.min(requestedPage, totalPages);
  const inferredPatientName = selectedFile ? inferPatientNameFromFilename(selectedFile.name) : "";
  const paginatedTasks = useMemo(() => {
    const start = (currentPage - 1) * PAGE_SIZE;
    return tasks.slice(start, start + PAGE_SIZE);
  }, [currentPage, tasks]);

  const pageStart = tasks.length === 0 ? 0 : (currentPage - 1) * PAGE_SIZE + 1;
  const pageEnd = Math.min(currentPage * PAGE_SIZE, tasks.length);

  function handleFileChange(file: File | null) {
    setSelectedFile(file);
    setUploadError(null);
    if (file) {
      setMeasureCodes(inferMeasureFromFilename(file.name));
    }
  }

  async function handleUploadSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedFile) {
      setUploadError("Choose a PDF file first.");
      return;
    }

    const formData = new FormData();
    formData.append("file", selectedFile);
    if (measureCodes) {
      formData.append("measure_codes", measureCodes);
    }

    try {
      setUploading(true);
      setUploadError(null);
      await importTaskPdf(formData);
      setUploadOpen(false);
      setSelectedFile(null);
      setMeasureCodes("");
      await loadTasks();
      showToast({
        title: "PDF imported successfully",
        description: "The chart is ready for extraction and reviewer triage.",
        tone: "success",
      });
    } catch (uploadFailure) {
      const message = uploadFailure instanceof Error ? uploadFailure.message : "Upload failed";
      setUploadError(message);
      showToast({
        title: "Upload failed",
        description: message,
        tone: "error",
      });
    } finally {
      setUploading(false);
    }
  }

  return (
    <MockAuthGate>
      <main className="mx-auto flex w-full max-w-[1480px] flex-1 flex-col gap-8 px-6 py-8 lg:px-8">
      <section className="overflow-hidden rounded-[28px] border border-white/70 bg-white px-6 py-5 shadow-md shadow-slate-900/5 lg:px-7">
        <div className="flex flex-col gap-5 xl:flex-row xl:items-center xl:justify-between">
          <div className="flex min-w-0 flex-col gap-2">
            <div className="inline-flex -mt-3 w-fit items-center rounded-full border border-blue-200 bg-blue-50 px-3 py-1 text-xs font-semibold uppercase tracking-[0.22em] text-blue-700">
              MedComply Agent
            </div>
            <h1 className="text-2xl font-semibold tracking-tight text-slate-900">Task Queue</h1>
          </div>

          <div className="flex flex-1 flex-col gap-4 xl:flex-row xl:items-center xl:justify-end">
            <div className="flex gap-3 overflow-x-auto pb-1 xl:justify-end">
              <MetricCard label="Total tasks" value={String(dashboardMetrics.total)} accent="bg-blue-500" />
              <MetricCard label="Open gaps" value={String(dashboardMetrics.openGaps)} accent="bg-rose-500" />
              <MetricCard label="Awaiting review" value={String(dashboardMetrics.awaitingReview)} accent="bg-sky-500" />
              <MetricCard label="Confirmed" value={String(dashboardMetrics.confirmed)} accent="bg-emerald-500" />
            </div>

            <button
              type="button"
              onClick={() => {
                setUploadOpen(true);
                setUploadError(null);
              }}
              className="inline-flex shrink-0 items-center justify-center rounded-xl bg-blue-600 px-5 py-3 text-sm font-semibold text-white shadow-sm shadow-blue-900/20 transition hover:bg-blue-700"
            >
              Upload PDF
            </button>
            <MockLogoutButton />
          </div>
        </div>
      </section>

      {loading ? <p className="text-sm text-slate-500">Loading tasks...</p> : null}
      {error ? <p className="rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">{error}</p> : null}

      {!loading && !error ? (
        <section className="overflow-hidden rounded-[28px] border border-white/70 bg-white shadow-md shadow-slate-900/5">
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead className="bg-slate-50 text-left text-slate-500">
                <tr>
                  <th className="px-6 py-4 font-semibold">Task ID</th>
                  <th className="px-6 py-4 font-semibold">Patient Name</th>
                  <th className="px-6 py-4 font-semibold">Document</th>
                  <th className="px-6 py-4 font-semibold">Workflow</th>
                  <th className="px-6 py-4 font-semibold">Measure</th>
                  <th className="px-6 py-4 font-semibold">Gap status</th>
                  <th className="px-6 py-4 font-semibold">Action</th>
                </tr>
              </thead>
              <tbody>
                {paginatedTasks.map((task) => (
                  <tr key={task.task_id} className="border-t border-slate-100 transition hover:bg-slate-50/70">
                    <td className="px-6 py-5 align-top">
                      <div className="text-sm font-semibold text-slate-900">#{task.task_id}</div>
                    </td>
                    <td className="px-6 py-5 align-top">
                      <div className="font-medium text-slate-800">{task.patient_name}</div>
                    </td>
                    <td className="px-6 py-5 align-top">
                      <div className="font-medium text-slate-800">{task.source_pdf_path.split("/").pop()}</div>
                    </td>
                    <td className="px-6 py-5 align-top">
                      <StatusPill label={task.status} tone={statusTone(task.status)} />
                    </td>
                    <td className="px-6 py-5 align-top">
                      <div className="flex flex-wrap gap-2">
                        {task.measures.length > 0 ? (
                          task.measures.map((measure) => (
                            <StatusPill key={measure} label={measure} tone="slate" />
                          ))
                        ) : (
                          <span className="text-sm text-slate-400">Not assigned</span>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-5 align-top">
                      <StatusPill label={task.gap_status ?? "Open"} tone={gapTone(task.gap_status)} />
                    </td>
                    <td className="px-6 py-5 align-top">
                      <Link
                        href={`/tasks/${task.task_id}`}
                        className="inline-flex items-center justify-center rounded-xl border border-blue-200 bg-blue-50 px-4 py-2 text-sm font-semibold text-blue-700 transition hover:border-blue-300 hover:bg-blue-100"
                      >
                        Enter Review
                      </Link>
                    </td>
                  </tr>
                ))}
                {tasks.length === 0 ? (
                  <tr>
                    <td className="px-6 py-10 text-center text-slate-500" colSpan={7}>
                      No tasks found.
                    </td>
                  </tr>
                ) : null}
              </tbody>
            </table>
          </div>
          {tasks.length > 0 ? (
            <div className="flex flex-col gap-3 border-t border-slate-100 px-6 py-4 text-sm text-slate-500 sm:flex-row sm:items-center sm:justify-between">
              <p>
                Showing {pageStart}-{pageEnd} of {tasks.length} tasks
              </p>
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={() => setRequestedPage((page) => Math.max(1, page - 1))}
                  disabled={currentPage === 1}
                  className="inline-flex items-center justify-center rounded-lg border border-slate-200 bg-white px-3 py-2 font-medium text-slate-700 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-45"
                >
                  Previous
                </button>
                <div className="flex items-center gap-1.5">
                  {Array.from({ length: totalPages }, (_, index) => index + 1).map((pageNumber) => (
                    <button
                      key={pageNumber}
                      type="button"
                      onClick={() => setRequestedPage(pageNumber)}
                      className={`inline-flex h-9 w-9 items-center justify-center rounded-lg border text-sm font-semibold transition ${
                        pageNumber === currentPage
                          ? "border-blue-600 bg-blue-600 text-white"
                          : "border-slate-200 bg-white text-slate-700 hover:bg-slate-50"
                      }`}
                    >
                      {pageNumber}
                    </button>
                  ))}
                </div>
                <button
                  type="button"
                  onClick={() => setRequestedPage((page) => Math.min(totalPages, page + 1))}
                  disabled={currentPage === totalPages}
                  className="inline-flex items-center justify-center rounded-lg border border-slate-200 bg-white px-3 py-2 font-medium text-slate-700 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-45"
                >
                  Next
                </button>
              </div>
            </div>
          ) : null}
        </section>
      ) : null}

      {uploadOpen ? (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/35 px-4 backdrop-blur-sm">
          <div className="w-full max-w-xl rounded-[28px] border border-white/80 bg-white p-7 shadow-2xl shadow-slate-900/15">
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.22em] text-blue-700">New intake</p>
                <h3 className="mt-2 text-2xl font-semibold tracking-tight text-slate-900">Upload chart PDF</h3>
                <p className="mt-2 text-sm leading-6 text-slate-500">
                  Use text-based EHR PDFs. The system can infer CBP/BPD/GSD from filename, or you can set the measure explicitly.
                </p>
              </div>
              <button
                type="button"
                onClick={() => setUploadOpen(false)}
                className="rounded-full border border-slate-200 px-3 py-1 text-sm text-slate-500 transition hover:border-slate-300 hover:text-slate-700"
              >
                Close
              </button>
            </div>

            <form className="mt-7 flex flex-col gap-5" onSubmit={handleUploadSubmit}>
              <label className="flex flex-col gap-2 text-sm font-semibold text-slate-700">
                PDF file
                <div className="rounded-xl border border-slate-300 bg-slate-50 px-4 py-3 transition focus-within:border-blue-500 focus-within:ring-2 focus-within:ring-blue-500/20">
                  <input
                    id="upload-pdf-input"
                    type="file"
                    accept="application/pdf"
                    onChange={(event) => handleFileChange(event.target.files?.[0] ?? null)}
                    className="sr-only"
                  />
                  <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                    <div className="min-w-0 text-sm font-medium text-slate-700">
                      <span className="block truncate">{selectedFile ? selectedFile.name : "No file selected"}</span>
                    </div>
                    <label
                      htmlFor="upload-pdf-input"
                      className="inline-flex shrink-0 cursor-pointer items-center justify-center rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-slate-800 transition hover:bg-slate-50"
                    >
                      Choose file
                    </label>
                  </div>
                </div>
              </label>

              <label className="flex flex-col gap-2 text-sm font-semibold text-slate-700">
                Patient name
                <div className="rounded-xl border border-slate-300 bg-slate-50 px-4 py-3 text-sm font-medium text-slate-700">
                  {inferredPatientName || "Will infer from filename"}
                </div>
              </label>

              <label className="flex flex-col gap-2 text-sm font-semibold text-slate-700">
                Target measure
                <div className="relative">
                  <select
                    value={measureCodes}
                    onChange={(event) => setMeasureCodes(event.target.value)}
                    className="w-full appearance-none rounded-xl border border-slate-300 bg-slate-50 px-4 py-3 pr-12 text-sm text-slate-700 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20"
                  >
                    <option value="">Auto from filename</option>
                    <option value="CBP">CBP</option>
                    <option value="BPD">BPD</option>
                    <option value="GSD">GSD</option>
                  </select>
                  <svg
                    viewBox="0 0 20 20"
                    fill="none"
                    aria-hidden="true"
                    className="pointer-events-none absolute right-4 top-1/2 h-5 w-5 -translate-y-1/2 text-slate-500"
                  >
                    <path
                      d="M5 7.5L10 12.5L15 7.5"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                  </svg>
                </div>
              </label>

              {uploadError ? <p className="text-sm text-rose-700">{uploadError}</p> : null}

              <div className="flex justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setUploadOpen(false)}
                  className="rounded-xl border border-slate-300 px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={uploading}
                  className="rounded-xl bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
                >
                  {uploading ? "Uploading..." : "Start Intake"}
                </button>
              </div>
            </form>
          </div>
        </div>
      ) : null}
      </main>
    </MockAuthGate>
  );
}
