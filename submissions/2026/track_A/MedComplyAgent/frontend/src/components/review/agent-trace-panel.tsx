"use client";

import { useState } from "react";

import { StatusPill } from "@/components/ui/status-pill";
import type { AgentTraceStep, LiveAgentTraceState } from "@/lib/review-mappers";

type AgentTracePanelProps = {
  steps: AgentTraceStep[];
  finalSummary: string | null;
  extracting: boolean;
  liveStep: LiveAgentTraceState | null;
};

export function AgentTracePanel({ steps, finalSummary, extracting, liveStep }: AgentTracePanelProps) {
  const [expanded, setExpanded] = useState(false);
  const visibleStep = liveStep;
  const stepCount = liveStep ? liveStep.total : steps.length;

  if (!visibleStep && !finalSummary && !extracting) {
    return null;
  }

  return (
    <section className="rounded-xl border border-slate-200 bg-white p-3">
      <div className="flex items-center justify-between gap-3">
        <div>
          <h3 className="text-base font-semibold text-slate-950">Agent Trace</h3>
          <p className="mt-0.5 text-xs text-slate-500">
            {extracting ? "Live extraction progress" : "Latest completed trace"}
          </p>
        </div>
        <div className="flex shrink-0 items-center gap-2">
          {stepCount > 0 ? <StatusPill label={`${stepCount} steps`} tone="blue" /> : null}
          {steps.length > 0 && !extracting ? (
            <button
              type="button"
              onClick={() => setExpanded((open) => !open)}
              className="inline-flex items-center gap-2 rounded-lg border border-blue-600 bg-white px-4 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
            >
              {expanded ? "Hide" : "Expand"}
              <svg
                viewBox="0 0 20 20"
                fill="none"
                aria-hidden="true"
                className={`h-4 w-4 shrink-0 transition-transform duration-200 ${expanded ? "rotate-180" : "rotate-0"}`}
              >
                <path
                  d="M5 7.5L10 12.5L15 7.5"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            </button>
          ) : null}
        </div>
      </div>

      {visibleStep ? (
        <div className="mt-3 rounded-lg border border-slate-200 bg-slate-50 px-3 py-3">
          <div className="flex items-start gap-3">
            {liveStep ? <ProgressRing progress={liveStep.progress} /> : <CompletedDot />}
            <div className="min-w-0 flex-1">
              <div className="flex flex-wrap items-center gap-2">
                <span className="text-sm font-semibold text-slate-950">{displayAction(visibleStep.action)}</span>
                <StatusPill label="running" tone="blue" />
              </div>
              {visibleStep.summary ? <p className="mt-1 text-sm leading-5 text-slate-700">{visibleStep.summary}</p> : null}
            </div>
          </div>
          {liveStep ? (
            <div className="mt-3 h-1.5 overflow-hidden rounded-full bg-slate-200">
              <div
                className="h-full rounded-full bg-blue-600 transition-all duration-500"
                style={{ width: `${liveStep.progress}%` }}
              />
            </div>
          ) : null}
        </div>
      ) : null}

      {!extracting && finalSummary ? (
        <div className="mt-3 rounded-lg border border-blue-200 bg-blue-50 px-3 py-2">
          <p className="text-xs font-semibold uppercase tracking-[0.12em] text-blue-700">Agent Summary</p>
          <p className="mt-1 text-sm leading-6 text-slate-800">{finalSummary}</p>
        </div>
      ) : null}

      {expanded && !extracting && steps.length > 0 ? (
        <div className="mt-3">
          <ol>
            {steps.map((step, index) => (
              <li key={step.stepId} className="grid grid-cols-[2rem_minmax(0,1fr)] gap-3">
                <div className="relative">
                  {index < steps.length - 1 ? (
                    <span className="absolute left-1/2 top-4 h-full w-px -translate-x-1/2 bg-slate-200" />
                  ) : null}
                  <span className="absolute left-1/2 top-1.5 h-2.5 w-2.5 -translate-x-1/2 rounded-full bg-blue-600 ring-4 ring-white" />
                </div>
                <div className="flex items-start justify-between gap-3 pb-4 last:pb-0">
                  <div className="min-w-0">
                    <div className="flex flex-wrap items-center gap-x-2 gap-y-1">
                      <span className="text-[11px] font-semibold uppercase tracking-[0.12em] text-slate-400">Step {index + 1}</span>
                      <span className="inline-flex items-center gap-1 text-xs font-medium text-emerald-700">
                        <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
                        {step.status}
                      </span>
                    </div>
                    <p className="mt-1 text-sm font-semibold leading-5 text-slate-900">{displayAction(step.action)}</p>
                    {step.summary ? <p className="mt-1 text-sm leading-5 text-slate-600">{step.summary}</p> : null}
                  </div>
                  <DetailsHover step={step} />
                </div>
              </li>
            ))}
          </ol>
        </div>
      ) : null}
    </section>
  );
}

function displayAction(action: string) {
  const labels: Record<string, string> = {
    get_encounter_info: "Checked encounter context",
    get_bp_readings: "Collected blood pressure evidence",
    get_lab_values: "Collected lab evidence",
    extract_clinical_evidence: "Structured clinical evidence",
    normalize_extraction_payload: "Prepared rule-ready payload",
  };

  return labels[action] ?? action.replaceAll("_", " ");
}

function DetailsHover({ step }: { step: AgentTraceStep }) {
  return (
    <div className="group relative ml-auto shrink-0">
      <button
        type="button"
        className="inline-flex h-7 w-7 items-center justify-center rounded-md text-slate-400 transition hover:bg-slate-100 hover:text-blue-700"
        title="Technical details"
      >
        <svg viewBox="0 0 20 20" fill="none" aria-hidden="true" className="h-4 w-4">
          <path d="M7.5 5.5L4 10L7.5 14.5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
          <path d="M12.5 5.5L16 10L12.5 14.5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
        <span className="sr-only">Technical details</span>
      </button>
      <div className="invisible absolute right-0 top-9 z-20 w-72 rounded-lg border border-slate-200 bg-white p-3 text-left opacity-0 shadow-lg transition group-focus-within:visible group-focus-within:opacity-100 group-hover:visible group-hover:opacity-100">
        <p className="text-xs font-semibold uppercase tracking-[0.12em] text-slate-500">Technical details</p>
        <dl className="mt-2 space-y-2 text-xs leading-5">
          <div>
            <dt className="font-semibold text-slate-500">Function</dt>
            <dd className="break-words font-mono text-slate-900">{step.action}</dd>
          </div>
          <div>
            <dt className="font-semibold text-slate-500">Outputs</dt>
            <dd className="break-words font-mono text-slate-900">{step.evidenceIds.length > 0 ? step.evidenceIds.join(", ") : "none"}</dd>
          </div>
          <div>
            <dt className="font-semibold text-slate-500">Memory</dt>
            <dd className="break-words font-mono text-slate-900">{step.memory || "No memory snapshot"}</dd>
          </div>
        </dl>
      </div>
    </div>
  );
}

function ProgressRing({ progress }: { progress: number }) {
  return (
    <div className="relative grid h-8 w-8 shrink-0 place-items-center rounded-full bg-blue-100">
      <div
        className="absolute inset-0 rounded-full"
        style={{
          background: `conic-gradient(rgb(37 99 235) ${progress * 3.6}deg, rgb(219 234 254) 0deg)`,
        }}
      />
      <div className="absolute inset-1 animate-pulse rounded-full bg-white" />
      <span className="relative h-2 w-2 rounded-full bg-blue-600" />
    </div>
  );
}

function CompletedDot() {
  return (
    <div className="grid h-8 w-8 shrink-0 place-items-center rounded-full bg-emerald-100">
      <span className="h-3 w-3 rounded-full bg-emerald-500" />
    </div>
  );
}
