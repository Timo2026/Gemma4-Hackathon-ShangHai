"use client";

import Link from "next/link";
import { useParams } from "next/navigation";

import { AgentTracePanel } from "@/components/review/agent-trace-panel";
import { ConclusionForm } from "@/components/review/conclusion-form";
import { EvidencePanel } from "@/components/review/evidence-panel";
import { PdfEvidenceViewer } from "@/components/pdf-evidence-viewer";
import { MockAuthGate, MockLogoutButton } from "@/components/ui/mock-auth-gate";
import { StatusPill } from "@/components/ui/status-pill";
import { useTaskReview } from "@/hooks/useTaskReview";
import { derivePatientName, isInteractiveTarget, sourceFilename, statusTone } from "@/lib/review-mappers";

export default function TaskReviewPage() {
  const params = useParams<{ taskId: string }>();
  const taskId = Number(params.taskId);
  const validTaskId = Number.isInteger(taskId) && taskId > 0;
  const review = useTaskReview(taskId, validTaskId);

  return (
    <MockAuthGate>
      <main
        className="mx-auto flex w-full max-w-[1600px] flex-col gap-4 px-4 py-4 xl:px-6 xl:py-5"
        onPointerDownCapture={(event) => {
          if (review.locateTarget && !isInteractiveTarget(event.target)) {
            review.setLocateTarget(null);
          }
        }}
      >
        <section className="rounded-[24px] border border-white/80 bg-white px-6 py-5 shadow-sm shadow-slate-900/5">
          <div className="flex flex-col gap-4 xl:flex-row xl:items-center xl:justify-between">
            <div>
              <h1 className="text-3xl font-semibold tracking-tight text-slate-950">
                Task Review {validTaskId ? `#${taskId}` : ""}
              </h1>
              {review.taskDetail ? (
                <div className="mt-2 flex flex-wrap items-center gap-x-3 gap-y-1 text-sm text-slate-600">
                  <span className="inline-flex items-center gap-1.5">
                    <span className="text-[11px] font-semibold uppercase tracking-[0.16em] text-slate-400">Patient</span>
                    <span className="font-medium text-slate-800">{derivePatientName(review.taskDetail)}</span>
                  </span>
                  <span className="text-slate-300">•</span>
                  {review.currentMeasureCode ? (
                    <>
                      <span className="inline-flex items-center gap-1.5">
                        <span className="text-[11px] font-semibold uppercase tracking-[0.16em] text-blue-600">Measure</span>
                        <span className="font-semibold text-blue-800">{review.currentMeasureCode}</span>
                      </span>
                      <span className="text-slate-300">•</span>
                    </>
                  ) : null}
                  <span className="inline-flex min-w-0 items-center gap-1.5">
                    <span className="shrink-0 text-[11px] font-semibold uppercase tracking-[0.16em] text-slate-400">
                      Source PDF
                    </span>
                    <span
                      className="truncate font-medium text-slate-700"
                      title={sourceFilename(review.taskDetail.source_pdf_path)}
                    >
                      {sourceFilename(review.taskDetail.source_pdf_path)}
                    </span>
                  </span>
                </div>
              ) : null}
            </div>

            <div className="flex flex-wrap items-center gap-3">
              <StatusPill label={review.status} tone={statusTone(review.status)} />
              <Link
                href="/"
                className="inline-flex items-center justify-center rounded-xl border border-slate-300 bg-white px-6 py-3 text-sm font-semibold text-slate-800 transition hover:bg-slate-50"
              >
                Back to Task List
              </Link>
              <MockLogoutButton />
            </div>
          </div>
        </section>

        {review.loading ? <p className="text-sm text-slate-500">Loading task detail...</p> : null}
        {review.error ? (
          <p className="rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">{review.error}</p>
        ) : null}

        {!review.loading && review.taskDetail ? (
          <div className="grid gap-5 xl:grid-cols-[minmax(420px,37fr)_minmax(0,63fr)] xl:items-start">
            <section className="flex min-h-0 flex-col rounded-[24px] border border-slate-200 bg-white shadow-sm shadow-slate-900/5 xl:overflow-hidden">
              <div className="flex shrink-0 items-center justify-between gap-3 border-b border-slate-100 px-6 py-4">
                <h2 className="text-lg font-semibold tracking-tight text-slate-950">Review Panel</h2>
                {review.canExtract ? (
                  <button
                    type="button"
                    onClick={() => void review.handleExtract()}
                    disabled={review.extracting || review.confirming}
                    className="inline-flex items-center justify-center rounded-xl bg-blue-600 px-6 py-3 text-sm font-semibold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
                  >
                    {review.extracting ? "Extracting..." : "Extract"}
                  </button>
                ) : null}
              </div>

              <div className="flex min-h-0 flex-1 flex-col gap-3 overflow-y-auto p-4">
                <AgentTracePanel
                  steps={review.agentTraceSteps}
                  finalSummary={review.agentFinalSummary}
                  extracting={review.extracting}
                  liveStep={review.liveAgentStep}
                />
                <EvidencePanel
                  showReviewContent={review.showReviewContent}
                  selectedEvidence={review.selectedEvidence}
                  readingEvidenceText={review.readingEvidenceText}
                  encounterEvidenceText={review.encounterEvidenceText}
                  dosEvidenceText={review.dosEvidenceText}
                  suggestionMeasureLabel={review.suggestionMeasureLabel}
                  suggestionStatusLabel={review.suggestionStatusLabel}
                  suggestionStatusTone={review.suggestionStatusTone}
                  suggestionSummaryText={review.suggestionSummaryText}
                  onLocate={review.handleLocate}
                />
                <ConclusionForm
                  historyOpen={review.historyOpen}
                  conclusionHistory={review.conclusionHistory}
                  nssdDraft={review.nssdDraft}
                  reviewerDecision={review.reviewerDecision}
                  reviewerNote={review.reviewerNote}
                  isConfirmed={review.isConfirmed}
                  confirming={review.confirming}
                  extracting={review.extracting}
                  currentMeasureCode={review.currentMeasureCode}
                  onToggleHistory={() => review.setHistoryOpen((open) => !open)}
                  onDraftChange={review.handleDraftChange}
                  onDecisionChange={review.setReviewerDecision}
                  onNoteChange={review.setReviewerNote}
                  onConfirm={() => void review.handleConfirm()}
                />
              </div>
            </section>

            <section className="flex h-[calc(100dvh-10.5rem)] min-h-[520px] flex-col overflow-hidden rounded-[24px] border border-slate-200 bg-white p-4 shadow-sm shadow-slate-900/5 xl:sticky xl:top-5">
              <div className="flex shrink-0 items-center justify-between gap-3 px-2 pb-4">
                <h2 className="text-lg font-semibold tracking-tight text-slate-950">Document Viewer</h2>
                <StatusPill label="PDF" tone="slate" />
              </div>

              <div className="min-h-0 flex-1 overflow-hidden rounded-[18px] border border-slate-300 bg-slate-100">
                <PdfEvidenceViewer
                  pdfUrl={review.taskDetail.source_pdf_path ? `/api/tasks/${taskId}/pdf` : null}
                  highlightTarget={review.locateTarget}
                  onLocateResult={review.handleLocateResult}
                />
              </div>
            </section>
          </div>
        ) : null}
      </main>
    </MockAuthGate>
  );
}
