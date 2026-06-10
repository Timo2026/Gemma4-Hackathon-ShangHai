import type {
  ExtractResponse,
  JsonObject,
  NssdCandidate,
  NssdPayload,
  ReviewerConclusionHistoryItem,
  SystemEvaluatedResult,
  TaskDetail,
  TaskStatus,
} from "@/lib/types";

export type ReviewerDecision = "GAP_CLOSED" | "GAP_OPEN" | "NEEDS_FOLLOW_UP";

export type EvidenceItem = {
  id: string;
  evidenceId?: string;
  title: string;
  date?: string;
  detail?: string;
  snippet?: string;
  encounterSnippet?: string;
  dateSnippet?: string;
  eligible: boolean;
  exclusionReason?: string;
};

export type NssdDraft = {
  patientName: string;
  dob: string;
  resultValue: string;
  dateOfService: string;
  provider: string;
  placeOfService: string;
  encounterType: string;
};

export type AgentTraceStep = {
  stepId: string;
  action: string;
  status: string;
  summary: string;
  evidenceIds: string[];
  memory: string;
};

export type LiveAgentTraceState = {
  stepId: string;
  action: string;
  summary: string;
  progress: number;
  index: number;
  total: number;
};

export type LocateTarget = {
  id: number;
  query: string;
  label: string;
};

export const decisionLabels: Record<ReviewerDecision, string> = {
  GAP_CLOSED: "Gap Closed",
  GAP_OPEN: "Gap Open",
  NEEDS_FOLLOW_UP: "Needs Follow-up",
};

export const emptyDraftOverrides: Partial<NssdDraft> = {};

const reasonCodeLabels: Record<string, string> = {
  BP_ABOVE_TARGET: "The selected blood pressure reading is above the measure target.",
  MISSING_HBA1C_DEFAULT_FAIL: "No HbA1c result was found, so this measure remains open.",
  HBA1C_ABOVE_TARGET: "The most recent HbA1c result is above the measure target.",
};

export function isJsonObject(value: unknown): value is JsonObject {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function isJsonObjectArray(value: unknown): JsonObject[] {
  return Array.isArray(value) ? value.filter(isJsonObject) : [];
}

function getString(value: JsonObject, key: string): string | undefined {
  const item = value[key];
  return typeof item === "string" ? item : undefined;
}

function getNumber(value: JsonObject, key: string): number | undefined {
  const item = value[key];
  return typeof item === "number" ? item : undefined;
}

export function extractEvaluations(result: ExtractResponse | null): SystemEvaluatedResult[] {
  if (!result) {
    return [];
  }

  if (result.system_evaluated_results.length > 0) {
    return result.system_evaluated_results;
  }

  return [
    {
      ...result.system_evaluated_result,
      measure_evaluation_id: result.measure_evaluation_id,
    },
  ];
}

export function detailEvaluation(detail: TaskDetail | null): SystemEvaluatedResult[] {
  const reviewEvaluation = detail?.review_state?.current_evaluation;
  if (reviewEvaluation) {
    return [reviewEvaluation];
  }

  if (!detail?.latest_evaluation || !isJsonObject(detail.latest_evaluation)) {
    return [];
  }

  const latest = detail.latest_evaluation;
  const evidencePayload = isJsonObject(latest.evidence_payload) ? latest.evidence_payload : {};
  const measureCode = typeof evidencePayload.measure_code === "string" ? evidencePayload.measure_code : "LATEST";
  const passFlag = typeof latest.pass_flag === "boolean" ? latest.pass_flag : false;
  const evaluationId = typeof latest.id === "number" ? latest.id : undefined;

  return [
    {
      measure_code: measureCode,
      pass_flag: passFlag,
      evidence_payload: evidencePayload,
      measure_evaluation_id: evaluationId,
    },
  ];
}

export function getStatus(detail: TaskDetail | null): TaskStatus | string {
  return detail?.status ?? "PENDING";
}

export function isSuggestedEvaluation(detail: TaskDetail | null): boolean {
  if (typeof detail?.review_state?.is_suggested === "boolean") {
    return detail.review_state.is_suggested;
  }

  if (!detail?.latest_evaluation || !isJsonObject(detail.latest_evaluation)) {
    return false;
  }

  const payload = isJsonObject(detail.latest_evaluation.evidence_payload) ? detail.latest_evaluation.evidence_payload : null;
  return payload?.is_suggested === true;
}

function systemDecision(evaluation: SystemEvaluatedResult | null): ReviewerDecision {
  return evaluation?.pass_flag ? "GAP_CLOSED" : "GAP_OPEN";
}

export function statusTone(status: string): "slate" | "blue" | "emerald" {
  if (status === "CONFIRMED") {
    return "emerald";
  }
  if (status === "EXTRACTED") {
    return "blue";
  }
  return "slate";
}

export function historyDecisionLabel(decision: string): string {
  if (decision in decisionLabels) {
    return decisionLabels[decision as ReviewerDecision];
  }
  return decision;
}

export function sourceFilename(path: string | undefined): string {
  return path?.split("/").at(-1) ?? "Unknown document";
}

export function derivePatientName(taskDetail: TaskDetail | null): string {
  if (taskDetail?.patient_name) {
    return taskDetail.patient_name;
  }

  const filename = sourceFilename(taskDetail?.source_pdf_path);
  const base = filename.replace(/\.pdf$/i, "");
  const parts = base.split("_").filter(Boolean);
  if (parts.length >= 2) {
    return `${parts[0]} ${parts[1]}`;
  }
  return taskDetail ? `Patient ${taskDetail.patient_id}` : "";
}

function detailLabel(detail?: string): string {
  return detail?.split(" · ")[0] ?? "";
}

export function buildEvidenceText(evidence: EvidenceItem | null, evaluation: SystemEvaluatedResult | null): string {
  if (evidence?.snippet?.trim()) {
    return evidence.snippet;
  }

  const selected = evaluation?.evidence_payload.selected_observation;
  if (isJsonObject(selected)) {
    const snippet = getString(selected, "snippet");
    if (snippet) {
      return snippet;
    }
  }

  return "No source evidence text found in the extraction payload.";
}

export function buildEncounterEvidenceText(
  evidence: EvidenceItem | null,
  fallbackEncounterType: string,
  candidate: NssdCandidate | null,
): string {
  if (evidence?.encounterSnippet?.trim()) {
    return evidence.encounterSnippet;
  }
  if (candidate?.encounter_snippet.trim()) {
    return candidate.encounter_snippet;
  }
  if (fallbackEncounterType.trim()) {
    return fallbackEncounterType;
  }
  if (evidence?.detail?.trim()) {
    return evidence.detail;
  }
  return "No encounter source text found in the extraction payload.";
}

export function buildDosEvidenceText(
  evidence: EvidenceItem | null,
  fallbackDos: string,
  candidate: NssdCandidate | null,
): string {
  if (evidence?.dateSnippet?.trim()) {
    return evidence.dateSnippet;
  }
  if (fallbackDos.trim()) {
    return fallbackDos;
  }
  if (evidence?.date?.trim()) {
    return evidence.date;
  }
  if (candidate?.date_snippet.trim()) {
    return candidate.date_snippet;
  }
  return "No DOS source text found in the extraction payload.";
}

export function selectedObservation(evaluation: SystemEvaluatedResult | null): JsonObject | null {
  const selected = evaluation?.evidence_payload.selected_observation;
  return isJsonObject(selected) ? selected : null;
}

function selectedBpReading(selected: JsonObject | null): string {
  if (!selected) {
    return "";
  }
  const explicitReading = getString(selected, "conclusion_reading");
  if (explicitReading) {
    return explicitReading;
  }

  const systolic = getNumber(selected, "lowest_systolic");
  const diastolic = getNumber(selected, "lowest_diastolic");
  return systolic !== undefined && diastolic !== undefined ? `${systolic}/${diastolic}` : "";
}

function selectedBpDos(selected: JsonObject | null): string {
  if (!selected) {
    return "";
  }
  return getString(selected, "dos") ?? getString(selected, "date") ?? "";
}

function isMissingDefaultObservation(selected: JsonObject | null): boolean {
  return selected?.is_default_value === true || selected?.value === null;
}

export function buildBpEvidenceReadingText(
  evidence: EvidenceItem | null,
  selected: JsonObject | null,
  fallbackText: string,
): string {
  const readings = isJsonObjectArray(selected?.evidence_readings);
  if (readings.length > 1) {
    return readings
      .map((reading, index) => {
        const label = getString(reading, "label") ?? `${index + 1}`;
        const value = getString(reading, "reading") ?? "BP reading";
        const snippet = getString(reading, "snippet");
        return snippet ? `${label}. ${snippet}` : `${label}. BP ${value}`;
      })
      .join("\n");
  }

  return evidence?.snippet?.trim() || evidence?.title || fallbackText;
}

export function buildSuggestionReason(evaluation: SystemEvaluatedResult | null, evidence: EvidenceItem | null): string {
  const reasons = buildFailureReasons(evaluation, evidence);
  if (reasons.length > 0) {
    return reasons.join(" ");
  }

  if (evaluation?.pass_flag) {
    return "Extracted evidence meets this measure rule.";
  }

  return "Extracted evidence does not meet this measure rule.";
}

function buildEncounterExclusionReason(evaluation: SystemEvaluatedResult | null, evidence: EvidenceItem | null): string | null {
  const ruleResult = isJsonObject(evaluation?.evidence_payload.rule_result) ? evaluation.evidence_payload.rule_result : null;
  const excludedCandidates = isJsonObjectArray(ruleResult?.bp_candidates_excluded);
  const encounterTypes = Array.from(
    new Set(
      excludedCandidates
        .map((candidate) => getString(candidate, "encounter_type")?.trim())
        .filter((value): value is string => Boolean(value)),
    ),
  );

  if (encounterTypes.length === 1) {
    return `${encounterTypes[0]} encounter is excluded for this measure, so no valid blood pressure reading remains.`;
  }

  if (encounterTypes.length > 1) {
    return `${encounterTypes.join(" and ")} encounters are excluded for this measure, so no valid blood pressure reading remains.`;
  }

  return evidence?.exclusionReason ?? "No valid blood pressure reading remains after encounter exclusions.";
}

function buildFailureReasons(evaluation: SystemEvaluatedResult | null, evidence: EvidenceItem | null): string[] {
  const reasonCodes = evaluation?.evidence_payload.reason_codes;
  const reasons = Array.isArray(reasonCodes)
    ? reasonCodes
        .filter((value): value is string => typeof value === "string")
        .map((value) => {
          if (value === "NO_VALID_BP_AFTER_EXCLUSION") {
            return buildEncounterExclusionReason(evaluation, evidence);
          }
          return reasonCodeLabels[value] ?? value.replaceAll("_", " ").toLowerCase();
        })
        .filter((value): value is string => Boolean(value))
    : [];

  const hasEncounterExclusionReason = Array.isArray(reasonCodes)
    ? reasonCodes.includes("NO_VALID_BP_AFTER_EXCLUSION")
    : false;

  if (
    !evaluation?.pass_flag &&
    evidence?.exclusionReason &&
    !hasEncounterExclusionReason &&
    !reasons.includes(evidence.exclusionReason)
  ) {
    reasons.push(evidence.exclusionReason);
  }
  return Array.from(new Set(reasons));
}

export function normalizeRequestErrorMessage(message: string): string {
  const trimmed = message.trim();

  if (/read operation timed out/i.test(trimmed) || /timed out/i.test(trimmed)) {
    return "Extraction timed out while waiting for the LLM response. Please try again.";
  }

  if (/^LLM extraction failed:/i.test(trimmed)) {
    const simplified = trimmed.replace(/^LLM extraction failed:\s*/i, "").replace(/^LLM request failed:\s*/i, "");
    return simplified || "Extraction failed. Please try again.";
  }

  return trimmed;
}

export function historyReading(item: ReviewerConclusionHistoryItem): string {
  return item.result_value || "-";
}

export function buildEvidenceItems(evaluation: SystemEvaluatedResult | null): EvidenceItem[] {
  if (!evaluation) {
    return [];
  }

  const payload = evaluation.evidence_payload;
  const selected = selectedObservation(evaluation);
  const selectedEvidenceReadings = isJsonObjectArray(selected?.evidence_readings);
  const showSelectedEvidenceReadingList = selectedEvidenceReadings.length > 1;
  const ruleResult = isJsonObject(payload.rule_result) ? payload.rule_result : {};
  const items: EvidenceItem[] = [];
  const allowedValues = Array.isArray(ruleResult.allowed_encounter_types)
    ? ruleResult.allowed_encounter_types.filter((value): value is string => typeof value === "string")
    : [];
  const hasEncounterFilter = allowedValues.length > 0;
  const allowedEncounterTypes = new Set(allowedValues);

  const bpCandidates = isJsonObjectArray(ruleResult.bp_candidates_all);
  const bpItemsSource = showSelectedEvidenceReadingList
    ? selectedEvidenceReadings
    : bpCandidates.length > 0
      ? bpCandidates
      : isJsonObjectArray(ruleResult.bp_candidates_kept);

  for (const [index, candidate] of bpItemsSource.entries()) {
    const systolic = getNumber(candidate, "systolic");
    const diastolic = getNumber(candidate, "diastolic");
    const date = getString(candidate, "date");
    const encounterType = getString(candidate, "encounter_type");
    const explicitReading = getString(candidate, "reading");
    const value = explicitReading ?? (systolic !== undefined && diastolic !== undefined ? `${systolic}/${diastolic}` : "BP reading");
    const eligible = hasEncounterFilter ? Boolean(encounterType && allowedEncounterTypes.has(encounterType)) : true;
    const exclusionReason = hasEncounterFilter
      ? eligible
        ? undefined
        : encounterType
          ? `${encounterType} is not allowed for this measure.`
          : "Encounter type is missing, so this reading cannot be used."
      : undefined;

    items.push({
      id: getString(candidate, "evidence_id") ?? `bp-${index}`,
      evidenceId: getString(candidate, "evidence_id"),
      title: showSelectedEvidenceReadingList ? `BP ${index + 1} ${value}` : `BP ${value}`,
      date,
      detail: encounterType,
      snippet: getString(candidate, "snippet"),
      encounterSnippet: getString(candidate, "encounter_snippet"),
      dateSnippet: showSelectedEvidenceReadingList ? date : getString(candidate, "date_snippet"),
      eligible,
      exclusionReason,
    });
  }

  if (isJsonObject(ruleResult.latest_hba1c)) {
    const latest = ruleResult.latest_hba1c;
    const value = getNumber(latest, "value");
    items.push({
      id: getString(latest, "evidence_id") ?? "latest-hba1c",
      evidenceId: getString(latest, "evidence_id"),
      title: value !== undefined ? `HbA1c ${value}%` : "HbA1c result",
      date: getString(latest, "date"),
      detail: getString(latest, "encounter_type") ?? getString(latest, "test_type"),
      snippet: getString(latest, "snippet"),
      encounterSnippet: getString(latest, "encounter_snippet"),
      dateSnippet: getString(latest, "date_snippet"),
      eligible: true,
    });
  }

  if (items.length === 0 && isJsonObject(payload.selected_observation)) {
    const selected = payload.selected_observation;
    const systolic = getNumber(selected, "lowest_systolic");
    const diastolic = getNumber(selected, "lowest_diastolic");
    const a1cValue = getNumber(selected, "value");
    const title =
      systolic !== undefined && diastolic !== undefined
        ? `BP ${systolic}/${diastolic}`
        : isMissingDefaultObservation(selected)
          ? "No HbA1c result found in chart"
          : a1cValue !== undefined
            ? `HbA1c ${a1cValue}%`
            : "Selected observation";

    items.push({
      id: getString(selected, "evidence_id") ?? "selected-observation",
      evidenceId: getString(selected, "evidence_id"),
      title,
      date: getString(selected, "date"),
      detail: getString(selected, "encounter_type") ?? getString(selected, "test_type"),
      snippet: getString(selected, "snippet"),
      encounterSnippet: getString(selected, "encounter_snippet"),
      dateSnippet: getString(selected, "date_snippet"),
      eligible: true,
    });
  }

  return items;
}

export function initialReviewerDecision(evaluation: SystemEvaluatedResult | null): ReviewerDecision {
  const conclusion = evaluation?.evidence_payload.reviewer_conclusion;
  if (isJsonObject(conclusion)) {
    const decision = conclusion.decision;
    if (decision === "GAP_CLOSED" || decision === "GAP_OPEN" || decision === "NEEDS_FOLLOW_UP") {
      return decision;
    }
  }

  return systemDecision(evaluation);
}

export function initialReviewerNote(evaluation: SystemEvaluatedResult | null): string {
  const conclusion = evaluation?.evidence_payload.reviewer_conclusion;
  if (isJsonObject(conclusion) && typeof conclusion.note === "string") {
    return conclusion.note;
  }
  return "";
}

function extractionPayload(extractResult: ExtractResponse | null, taskDetail: TaskDetail | null): JsonObject | null {
  if (extractResult && isJsonObject(extractResult.raw_extraction)) {
    return extractResult.raw_extraction;
  }

  if (taskDetail?.review_state?.extraction_payload && isJsonObject(taskDetail.review_state.extraction_payload)) {
    return taskDetail.review_state.extraction_payload;
  }

  if (!taskDetail?.latest_extraction || !isJsonObject(taskDetail.latest_extraction)) {
    return null;
  }

  const extractedPayload = taskDetail.latest_extraction.extracted_payload;
  return isJsonObject(extractedPayload) ? extractedPayload : null;
}

export function extractNssdCandidates(extractResult: ExtractResponse | null, taskDetail: TaskDetail | null): NssdCandidate[] {
  const payload = extractionPayload(extractResult, taskDetail);
  if (!payload) {
    return [];
  }

  const candidates = isJsonObjectArray(payload.nssd_candidates);
  return candidates.map((item) => ({
    evidence_id: getString(item, "evidence_id") ?? "",
    patient_name: getString(item, "patient_name") ?? "",
    dob: getString(item, "dob") ?? "",
    result_value: getString(item, "result_value") ?? "",
    dos: getString(item, "dos") ?? "",
    rendering_provider: getString(item, "rendering_provider") ?? "",
    place_of_service: getString(item, "place_of_service") ?? "",
    encounter_type: getString(item, "encounter_type") ?? "Unknown",
    measure_hint: getString(item, "measure_hint") ?? "",
    snippet: getString(item, "snippet") ?? "",
    encounter_snippet: getString(item, "encounter_snippet") ?? "",
    date_snippet: getString(item, "date_snippet") ?? "",
  }));
}

export function extractAgentTraceFinalSummary(
  extractResult: ExtractResponse | null,
  taskDetail: TaskDetail | null,
): string | null {
  const payload = extractionPayload(extractResult, taskDetail);
  const trace = isJsonObject(payload?.agent_trace) ? payload.agent_trace : null;
  const summary = getString(trace ?? {}, "final_summary")?.trim();
  return summary || null;
}

export function extractAgentTraceSteps(extractResult: ExtractResponse | null, taskDetail: TaskDetail | null): AgentTraceStep[] {
  const payload = extractionPayload(extractResult, taskDetail);
  const trace = isJsonObject(payload?.agent_trace) ? payload.agent_trace : null;
  const steps = isJsonObjectArray(trace?.steps);

  return steps.map((step, index) => {
    const rawEvidenceIds = Array.isArray(step.output_evidence_ids)
      ? step.output_evidence_ids.filter((value): value is string => typeof value === "string")
      : [];

    return {
      stepId: getString(step, "step_id") ?? `step-${index + 1}`,
      action: getString(step, "action") ?? "agent_step",
      status: getString(step, "status") ?? "completed",
      summary: getString(step, "summary") ?? "",
      evidenceIds: rawEvidenceIds,
      memory: getString(step, "memory") ?? "",
    };
  });
}

export function matchNssdCandidate(
  candidates: NssdCandidate[],
  selectedEvidence: EvidenceItem | null,
  measureCode: string | null,
): NssdCandidate | null {
  if (candidates.length === 0) {
    return null;
  }

  const snippet = selectedEvidence?.snippet?.trim().toLowerCase();
  if (snippet) {
    const bySnippet = candidates.find((item) => item.snippet.trim().toLowerCase() === snippet);
    if (bySnippet) {
      return bySnippet;
    }
  }

  const date = selectedEvidence?.date?.trim();
  if (date) {
    const byDate = candidates.find((item) => item.dos.trim() === date);
    if (byDate) {
      return byDate;
    }
  }

  if (measureCode) {
    const byMeasure = candidates.find((item) => item.measure_hint === measureCode);
    if (byMeasure) {
      return byMeasure;
    }
  }

  return candidates[0];
}

export function savedNssdPayload(taskDetail: TaskDetail | null): NssdPayload | null {
  const reviewNssdPayload = taskDetail?.review_state?.nssd_payload;
  if (reviewNssdPayload && isJsonObject(reviewNssdPayload)) {
    return {
      patient_name: getString(reviewNssdPayload, "patient_name") ?? "",
      dob: getString(reviewNssdPayload, "dob") ?? "",
      result_value: getString(reviewNssdPayload, "result_value") ?? "",
      dos: getString(reviewNssdPayload, "dos") ?? "",
      rendering_provider:
        getString(reviewNssdPayload, "rendering_provider") ?? getString(reviewNssdPayload, "provider") ?? "",
      place_of_service: getString(reviewNssdPayload, "place_of_service") ?? "",
      encounter_type: getString(reviewNssdPayload, "encounter_type") ?? "",
    };
  }

  if (!taskDetail?.latest_evaluation || !isJsonObject(taskDetail.latest_evaluation)) {
    return null;
  }

  const payload = isJsonObject(taskDetail.latest_evaluation.evidence_payload)
    ? taskDetail.latest_evaluation.evidence_payload
    : null;
  if (!payload) {
    return null;
  }

  const nssdPayload = isJsonObject(payload.nssd_payload)
    ? payload.nssd_payload
    : isJsonObject(payload.reviewer_conclusion) && isJsonObject(payload.reviewer_conclusion.nssd_form)
      ? payload.reviewer_conclusion.nssd_form
      : null;

  if (!nssdPayload) {
    return null;
  }

  return {
    patient_name: getString(nssdPayload, "patient_name") ?? "",
    dob: getString(nssdPayload, "dob") ?? "",
    result_value: getString(nssdPayload, "result_value") ?? "",
    dos: getString(nssdPayload, "dos") ?? "",
    rendering_provider:
      getString(nssdPayload, "rendering_provider") ?? getString(nssdPayload, "provider") ?? "",
    place_of_service: getString(nssdPayload, "place_of_service") ?? "",
    encounter_type: getString(nssdPayload, "encounter_type") ?? "",
  };
}

export function buildDraft(
  taskDetail: TaskDetail | null,
  evaluation: SystemEvaluatedResult | null,
  selectedEvidence: EvidenceItem | null,
  selectedCandidate: NssdCandidate | null,
  savedPayload: NssdPayload | null,
): NssdDraft {
  const selected = selectedObservation(evaluation);
  const bpReading = selectedBpReading(selected);
  const bpDos = selectedBpDos(selected);

  const selectedEvidenceValue = isMissingDefaultObservation(selected)
    ? ""
    : selectedEvidence?.title.replace(/^BP\s+(?:\d+\s+)?/, "").replace(/^HbA1c\s+/, "") || "";

  return {
    patientName: selectedCandidate?.patient_name || savedPayload?.patient_name || derivePatientName(taskDetail),
    dob: selectedCandidate?.dob || savedPayload?.dob || "",
    resultValue:
      bpReading ||
      selectedCandidate?.result_value ||
      savedPayload?.result_value ||
      selectedEvidenceValue,
    dateOfService: bpDos || selectedCandidate?.dos || savedPayload?.dos || selectedEvidence?.date || "",
    provider: selectedCandidate?.rendering_provider || savedPayload?.rendering_provider || "",
    placeOfService:
      selectedCandidate?.place_of_service || savedPayload?.place_of_service || detailLabel(selectedEvidence?.detail),
    encounterType:
      selectedCandidate?.encounter_type || savedPayload?.encounter_type || detailLabel(selectedEvidence?.detail) || "",
  };
}

export function buildNssdPayload(draft: NssdDraft): NssdPayload {
  return {
    patient_name: draft.patientName,
    dob: draft.dob,
    result_value: draft.resultValue,
    dos: draft.dateOfService,
    rendering_provider: draft.provider,
    place_of_service: draft.placeOfService,
    encounter_type: draft.encounterType || draft.placeOfService,
  };
}

export function isInteractiveTarget(target: EventTarget | null): boolean {
  if (!(target instanceof HTMLElement)) {
    return false;
  }
  return Boolean(
    target.closest(
      'button, a, input, textarea, select, option, summary, [role="button"], [role="link"], [contenteditable="true"]',
    ),
  );
}
