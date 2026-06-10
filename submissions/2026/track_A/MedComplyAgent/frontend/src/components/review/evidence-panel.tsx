import { StatusPill } from "@/components/ui/status-pill";
import type { EvidenceItem } from "@/lib/review-mappers";

type EvidencePanelProps = {
  showReviewContent: boolean;
  selectedEvidence: EvidenceItem | null;
  readingEvidenceText: string;
  encounterEvidenceText: string;
  dosEvidenceText: string;
  suggestionMeasureLabel: string;
  suggestionStatusLabel: string;
  suggestionStatusTone: "emerald" | "rose";
  suggestionSummaryText: string | null;
  onLocate: (label: string, text: string) => void;
};

function EvidenceRow({
  label,
  text,
  onLocate,
}: {
  label: string;
  text: string;
  onLocate: () => void;
}) {
  return (
    <div className="grid grid-cols-[7.5rem_minmax(0,1fr)_auto] items-start gap-3 px-3 py-2.5">
      <p className="pt-2 text-xs font-semibold uppercase tracking-[0.12em] text-slate-500">{label}</p>
      <p className="min-w-0 whitespace-pre-wrap text-sm leading-6 text-slate-900">{text}</p>
      <button
        type="button"
        onClick={onLocate}
        className="shrink-0 rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-sm font-semibold text-slate-800 transition hover:bg-slate-50"
      >
        Locate
      </button>
    </div>
  );
}

export function EvidencePanel({
  showReviewContent,
  readingEvidenceText,
  encounterEvidenceText,
  dosEvidenceText,
  suggestionMeasureLabel,
  suggestionStatusLabel,
  suggestionStatusTone,
  suggestionSummaryText,
  onLocate,
}: EvidencePanelProps) {
  const reasonToneClasses =
    suggestionStatusTone === "emerald"
      ? "border-emerald-200 bg-emerald-50 text-emerald-800"
      : "border-rose-200 bg-rose-50 text-rose-700";
  const labelToneClass = suggestionStatusTone === "emerald" ? "text-emerald-700" : "text-rose-700";

  return (
    <section className="rounded-xl border border-slate-200 bg-white p-3">
      <div className="mb-3 flex items-center justify-between gap-3">
        <h3 className="text-base font-semibold text-slate-950">Review Evidence</h3>
      </div>
      {showReviewContent ? (
        <div className="space-y-3">
          <div className="divide-y divide-slate-100 rounded-lg border border-slate-200 bg-white">
            <EvidenceRow label="Reading" text={readingEvidenceText} onLocate={() => onLocate("Reading", readingEvidenceText)} />
            <EvidenceRow
              label="Encounter type"
              text={encounterEvidenceText}
              onLocate={() => onLocate("Encounter type", encounterEvidenceText)}
            />
            <EvidenceRow label="DOS" text={dosEvidenceText} onLocate={() => onLocate("DOS", dosEvidenceText)} />
          </div>

          <div className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-3">
            <div className="flex flex-wrap items-center gap-2">
              <p className="mr-1 text-xs font-semibold uppercase tracking-[0.12em] text-slate-500">System Suggestion</p>
              <StatusPill label={suggestionMeasureLabel} tone="slate" />
              <StatusPill label={suggestionStatusLabel} tone={suggestionStatusTone} />
            </div>
            {suggestionSummaryText ? (
              <div className={`mt-3 rounded-lg border px-3 py-2 ${reasonToneClasses}`}>
                <p className={`text-xs font-semibold uppercase tracking-[0.12em] ${labelToneClass}`}>Reason</p>
                <p className="mt-1 text-sm leading-6">{suggestionSummaryText}</p>
              </div>
            ) : null}
          </div>
        </div>
      ) : (
        <p className="rounded-xl border border-dashed border-slate-300 bg-slate-50 px-4 py-5 text-sm text-slate-500">
          Run Extract to load evidence text from the chart.
        </p>
      )}
    </section>
  );
}
