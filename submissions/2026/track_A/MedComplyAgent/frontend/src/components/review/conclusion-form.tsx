import { StatusPill } from "@/components/ui/status-pill";
import {
  decisionLabels,
  historyDecisionLabel,
  historyReading,
  type NssdDraft,
  type ReviewerDecision,
} from "@/lib/review-mappers";
import type { ReviewerConclusionHistoryItem } from "@/lib/types";

type ConclusionFormProps = {
  historyOpen: boolean;
  conclusionHistory: ReviewerConclusionHistoryItem[];
  nssdDraft: NssdDraft;
  reviewerDecision: ReviewerDecision;
  reviewerNote: string;
  isConfirmed: boolean;
  confirming: boolean;
  extracting: boolean;
  currentMeasureCode: string | null;
  onToggleHistory: () => void;
  onDraftChange: (field: keyof NssdDraft, value: string) => void;
  onDecisionChange: (decision: ReviewerDecision) => void;
  onNoteChange: (value: string) => void;
  onConfirm: () => void;
};

export function ConclusionForm({
  historyOpen,
  conclusionHistory,
  nssdDraft,
  reviewerDecision,
  reviewerNote,
  isConfirmed,
  confirming,
  extracting,
  currentMeasureCode,
  onToggleHistory,
  onDraftChange,
  onDecisionChange,
  onNoteChange,
  onConfirm,
}: ConclusionFormProps) {
  return (
    <section className="rounded-xl border border-slate-200 bg-white p-3">
      <div className="flex items-center justify-between gap-3">
        <h3 className="text-base font-semibold text-slate-950">Conclusion</h3>
        <button
          type="button"
          onClick={onToggleHistory}
          className="inline-flex items-center gap-2 rounded-lg border border-blue-600 bg-white px-4 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
        >
          History
          <svg
            viewBox="0 0 20 20"
            fill="none"
            aria-hidden="true"
            className={`h-4 w-4 shrink-0 transition-transform duration-200 ${historyOpen ? "rotate-180" : "rotate-0"}`}
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
      </div>

      {historyOpen ? (
        conclusionHistory.length > 0 ? (
          <div className="mt-3 overflow-hidden rounded-xl border border-slate-200">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-50 text-xs font-semibold text-slate-700">
                <tr>
                  <th className="px-4 py-3">Reading</th>
                  <th className="px-4 py-3">DOS</th>
                  <th className="px-4 py-3">Gap Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 bg-white">
                {conclusionHistory.map((item) => (
                  <tr key={item.measure_evaluation_id} className={item.is_current_active_status ? "bg-emerald-50/50" : undefined}>
                    <td className="px-4 py-3 font-medium text-slate-950">
                      <div className="flex flex-wrap items-center gap-2">
                        <span>{historyReading(item)}</span>
                        {item.is_current_active_status ? <StatusPill label="Current" tone="emerald" /> : null}
                      </div>
                    </td>
                    <td className="px-4 py-3 text-slate-700">{item.dos || "-"}</td>
                    <td className="px-4 py-3">
                      <StatusPill
                        label={historyDecisionLabel(item.decision).replace("Gap ", "")}
                        tone={item.decision === "GAP_CLOSED" ? "emerald" : item.decision === "GAP_OPEN" ? "rose" : "amber"}
                      />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="mt-3 rounded-xl border border-dashed border-slate-300 bg-slate-50 px-4 py-3 text-sm text-slate-500">
            No confirmed reviewer history for this patient yet.
          </p>
        )
      ) : null}

      <div className="mt-3 grid gap-3 sm:grid-cols-2">
        <DraftInput
          label="Patient"
          value={nssdDraft.patientName}
          disabled={isConfirmed}
          onChange={(value) => onDraftChange("patientName", value)}
        />
        <DraftInput label="DOB" value={nssdDraft.dob} disabled={isConfirmed} onChange={(value) => onDraftChange("dob", value)} />
        <DraftInput
          label="Reading"
          value={nssdDraft.resultValue}
          disabled={isConfirmed}
          onChange={(value) => onDraftChange("resultValue", value)}
        />
        <DraftInput
          label="DOS"
          value={nssdDraft.dateOfService}
          disabled={isConfirmed}
          onChange={(value) => onDraftChange("dateOfService", value)}
        />
        <DraftInput
          label="Provider"
          value={nssdDraft.provider}
          disabled={isConfirmed}
          onChange={(value) => onDraftChange("provider", value)}
        />
        <DraftInput
          label="Encounter Type"
          value={nssdDraft.encounterType}
          disabled={isConfirmed}
          onChange={(value) => onDraftChange("encounterType", value)}
        />
      </div>

      <div className="mt-3 grid grid-cols-3 overflow-hidden rounded-xl border border-slate-200" role="radiogroup">
        {(Object.keys(decisionLabels) as ReviewerDecision[]).map((decision) => {
          const selected = reviewerDecision === decision;
          const disabled = isConfirmed || confirming;
          return (
            <button
              key={decision}
              type="button"
              role="radio"
              aria-checked={selected}
              disabled={disabled}
              onClick={() => onDecisionChange(decision)}
              className={`border-r border-slate-200 px-3 py-3 text-center text-sm font-semibold transition last:border-r-0 ${
                selected ? "bg-blue-50 text-blue-800" : "bg-white text-slate-600 hover:bg-slate-50"
              } ${disabled ? "cursor-default opacity-70" : "cursor-pointer"}`}
            >
              {decisionLabels[decision].replace("Gap ", "")}
            </button>
          );
        })}
      </div>

      <div className="mt-3 grid gap-3 sm:grid-cols-[minmax(0,1fr)_auto] sm:items-end">
        <label className="flex flex-col gap-1.5 text-xs font-semibold text-slate-700" htmlFor="reviewer-note">
          Note
          <textarea
            id="reviewer-note"
            value={reviewerNote}
            onChange={(event) => onNoteChange(event.target.value)}
            disabled={isConfirmed || confirming}
            rows={4}
            className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-800 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 disabled:bg-slate-100"
          />
        </label>

        {!isConfirmed ? (
          <button
            type="button"
            onClick={onConfirm}
            disabled={confirming || extracting || !currentMeasureCode}
            className="inline-flex items-center justify-center rounded-xl bg-emerald-600 px-6 py-3 text-sm font-semibold text-white transition hover:bg-emerald-700 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {confirming ? "Confirming..." : "Confirm"}
          </button>
        ) : null}
      </div>
    </section>
  );
}

function DraftInput({
  label,
  value,
  disabled,
  onChange,
}: {
  label: string;
  value: string;
  disabled: boolean;
  onChange: (value: string) => void;
}) {
  return (
    <label className="flex flex-col gap-1.5 text-xs font-semibold text-slate-700">
      {label}
      <input
        value={value}
        onChange={(event) => onChange(event.target.value)}
        disabled={disabled}
        className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-800 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 disabled:bg-slate-100"
      />
    </label>
  );
}
