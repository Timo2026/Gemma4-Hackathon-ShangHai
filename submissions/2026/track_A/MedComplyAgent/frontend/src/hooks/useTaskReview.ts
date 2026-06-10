"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

import { useToast } from "@/components/ui/toast-provider";
import { confirmTask, extractTask, getTask } from "@/lib/api";
import {
  buildBpEvidenceReadingText,
  buildDraft,
  buildDosEvidenceText,
  buildEncounterEvidenceText,
  buildEvidenceItems,
  buildEvidenceText,
  buildNssdPayload,
  buildSuggestionReason,
  detailEvaluation,
  emptyDraftOverrides,
  extractAgentTraceFinalSummary,
  extractAgentTraceSteps,
  extractEvaluations,
  extractNssdCandidates,
  getStatus,
  initialReviewerDecision,
  initialReviewerNote,
  isSuggestedEvaluation,
  matchNssdCandidate,
  normalizeRequestErrorMessage,
  savedNssdPayload,
  selectedObservation,
  type LocateTarget,
  type LiveAgentTraceState,
  type NssdDraft,
  type ReviewerDecision,
} from "@/lib/review-mappers";
import type { ExtractResponse, TaskDetail } from "@/lib/types";

const LIVE_STEP_INTERVAL_MS = 2800;

type LiveAgentTraceTemplate = {
  action: string;
  summary: string;
};

function liveTraceTemplates(measureCode: string | null): LiveAgentTraceTemplate[] {
  const normalized = measureCode?.toUpperCase();
  const evidenceStep =
    normalized === "GSD"
      ? { action: "get_lab_values", summary: "Collecting HbA1c lab evidence for the target measure." }
      : { action: "get_bp_readings", summary: "Collecting blood pressure readings and source evidence." };

  return [
    { action: "get_encounter_info", summary: "Reviewing encounter context, patient identity, and date of service." },
    evidenceStep,
    { action: "extract_clinical_evidence", summary: "Structuring clinical evidence and audit snippets." },
    { action: "normalize_extraction_payload", summary: "Normalizing evidence ids, NSSD fields, and rule-ready payload." },
  ];
}

function buildLiveTraceStep(templates: LiveAgentTraceTemplate[], index: number): LiveAgentTraceState {
  const safeIndex = Math.min(Math.max(index, 0), templates.length - 1);
  const template = templates[safeIndex];
  return {
    stepId: `live-step-${safeIndex + 1}`,
    action: template.action,
    summary: template.summary,
    progress: Math.round(((safeIndex + 1) / templates.length) * 100),
    index: safeIndex,
    total: templates.length,
  };
}

export function useTaskReview(taskId: number, validTaskId: boolean) {
  const [taskDetail, setTaskDetail] = useState<TaskDetail | null>(null);
  const [extractResult, setExtractResult] = useState<ExtractResponse | null>(null);
  const [selectedEvidenceId, setSelectedEvidenceId] = useState<string | null>(null);
  const [reviewerDecision, setReviewerDecision] = useState<ReviewerDecision>("GAP_CLOSED");
  const [reviewerNote, setReviewerNote] = useState("");
  const [historyOpen, setHistoryOpen] = useState(false);
  const [draftOverrides, setDraftOverrides] = useState<Partial<NssdDraft>>(emptyDraftOverrides);
  const [locateTarget, setLocateTarget] = useState<LocateTarget | null>(null);
  const [loading, setLoading] = useState(true);
  const [extracting, setExtracting] = useState(false);
  const [confirming, setConfirming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [liveAgentStep, setLiveAgentStep] = useState<LiveAgentTraceState | null>(null);
  const { showToast } = useToast();

  const evaluations = useMemo(() => {
    const fromExtract = extractEvaluations(extractResult);
    if (fromExtract.length > 0) {
      return fromExtract;
    }
    return detailEvaluation(taskDetail);
  }, [extractResult, taskDetail]);

  const isLinkedSuggestion = isSuggestedEvaluation(taskDetail);
  const selectedEvaluation = evaluations[0] ?? null;
  const displayEvaluation = isLinkedSuggestion ? null : selectedEvaluation;
  const selectedBpObservation = selectedObservation(displayEvaluation);
  const evidenceItems = useMemo(() => buildEvidenceItems(displayEvaluation), [displayEvaluation]);
  const selectedEvidence = evidenceItems.find((item) => item.id === selectedEvidenceId) ?? evidenceItems[0] ?? null;
  const evidenceText = useMemo(() => buildEvidenceText(selectedEvidence, displayEvaluation), [selectedEvidence, displayEvaluation]);
  const readingEvidenceText = useMemo(
    () => buildBpEvidenceReadingText(selectedEvidence, selectedBpObservation, evidenceText),
    [selectedEvidence, selectedBpObservation, evidenceText],
  );
  const suggestionReason = useMemo(
    () => buildSuggestionReason(displayEvaluation, selectedEvidence),
    [displayEvaluation, selectedEvidence],
  );
  const currentMeasureCode =
    selectedEvaluation?.measure_code ?? taskDetail?.review_state?.current_measure_code ?? taskDetail?.measures[0] ?? null;
  const suggestionMeasureLabel = currentMeasureCode ?? "Measure";
  const suggestionStatusLabel = selectedEvaluation ? (selectedEvaluation.pass_flag ? "Gap Closed" : "Gap Open") : "Open";
  const suggestionStatusTone: "emerald" | "rose" = selectedEvaluation?.pass_flag ? "emerald" : "rose";
  const suggestionSummaryText = selectedEvaluation && !isLinkedSuggestion ? suggestionReason : null;
  const nssdCandidates = useMemo(() => extractNssdCandidates(extractResult, taskDetail), [extractResult, taskDetail]);
  const agentTraceSteps = useMemo(() => extractAgentTraceSteps(extractResult, taskDetail), [extractResult, taskDetail]);
  const agentFinalSummary = useMemo(
    () => extractAgentTraceFinalSummary(extractResult, taskDetail),
    [extractResult, taskDetail],
  );
  const matchedCandidate = useMemo(
    () => matchNssdCandidate(nssdCandidates, selectedEvidence, currentMeasureCode),
    [nssdCandidates, selectedEvidence, currentMeasureCode],
  );
  const persistedNssd = useMemo(() => (isLinkedSuggestion ? null : savedNssdPayload(taskDetail)), [isLinkedSuggestion, taskDetail]);
  const nssdDraft = useMemo(
    () => ({ ...buildDraft(taskDetail, displayEvaluation, selectedEvidence, matchedCandidate, persistedNssd), ...draftOverrides }),
    [taskDetail, displayEvaluation, selectedEvidence, matchedCandidate, persistedNssd, draftOverrides],
  );
  const encounterEvidenceText = useMemo(
    () => buildEncounterEvidenceText(selectedEvidence, nssdDraft.encounterType, matchedCandidate),
    [selectedEvidence, nssdDraft.encounterType, matchedCandidate],
  );
  const dosEvidenceText = useMemo(
    () => buildDosEvidenceText(selectedEvidence, nssdDraft.dateOfService, matchedCandidate),
    [selectedEvidence, nssdDraft.dateOfService, matchedCandidate],
  );
  const status = getStatus(taskDetail);
  const isExtracted = status === "EXTRACTED";
  const isConfirmed = status === "CONFIRMED";
  const canExtract = !isConfirmed;
  const showReviewContent = isExtracted || isConfirmed;
  const conclusionHistory = (taskDetail?.reviewer_conclusion_history ?? []).filter(
    (item) => item.measure_evaluation_id !== selectedEvaluation?.measure_evaluation_id,
  );

  useEffect(() => {
    if (!extracting || !liveAgentStep) {
      return;
    }

    const templates = liveTraceTemplates(currentMeasureCode);
    const timer = window.setInterval(() => {
      setLiveAgentStep((current) => {
        if (!current) {
          return current;
        }
        return buildLiveTraceStep(templates, Math.min(current.index + 1, templates.length - 1));
      });
    }, LIVE_STEP_INTERVAL_MS);

    return () => window.clearInterval(timer);
  }, [currentMeasureCode, extracting, liveAgentStep]);

  useEffect(() => {
    if (!validTaskId) {
      return;
    }

    let cancelled = false;

    async function loadTask() {
      try {
        setLoading(true);
        const detail = await getTask(taskId);
        if (cancelled) {
          return;
        }
        setTaskDetail(detail);
        setExtractResult(null);

        const initialEvaluation = detailEvaluation(detail)[0] ?? null;
        setReviewerDecision(initialReviewerDecision(initialEvaluation));
        setReviewerNote(initialReviewerNote(initialEvaluation));
        setSelectedEvidenceId(null);
        setDraftOverrides(emptyDraftOverrides);
        setError(null);
      } catch (loadError) {
        if (!cancelled) {
          setError(loadError instanceof Error ? loadError.message : "Failed to load task detail");
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    void loadTask();

    return () => {
      cancelled = true;
    };
  }, [taskId, validTaskId]);

  const refreshTask = useCallback(async () => {
    const detail = await getTask(taskId);
    setTaskDetail(detail);
    setExtractResult(null);
    return detail;
  }, [taskId]);

  const handleExtract = useCallback(async () => {
    if (!validTaskId || !canExtract) {
      return;
    }

    try {
      setExtracting(true);
      setLiveAgentStep(buildLiveTraceStep(liveTraceTemplates(currentMeasureCode), 0));
      const result = await extractTask(taskId);
      setExtractResult(result);

      const extracted = extractEvaluations(result);
      const firstEvaluation = extracted[0] ?? null;
      setReviewerDecision(initialReviewerDecision(firstEvaluation));
      setReviewerNote("");
      setSelectedEvidenceId(null);
      setDraftOverrides(emptyDraftOverrides);
      setError(null);
      await refreshTask();

      const closedMeasures = extracted.filter((item) => item.pass_flag).map((item) => item.measure_code);
      if (closedMeasures.length > 1) {
        showToast({
          title: `Success: ${closedMeasures[0]} closed`,
          description: `Linked measure ${closedMeasures.slice(1).join(", ")} also closed automatically.`,
          tone: "success",
        });
      } else {
        showToast({
          title: "Extraction refreshed",
          description: "The reviewer workspace was updated with the latest chart evidence.",
          tone: closedMeasures.length > 0 ? "success" : "info",
        });
      }
    } catch (extractError) {
      setExtractResult(null);
      try {
        await refreshTask();
      } catch {
        // Keep the request error below as the primary message.
      }
      const rawMessage = extractError instanceof Error ? extractError.message : "Extract request failed";
      const message = normalizeRequestErrorMessage(rawMessage);
      setError(message);
      showToast({
        title: "Extraction failed",
        description: message,
        tone: "error",
      });
    } finally {
      setLiveAgentStep(null);
      setExtracting(false);
    }
  }, [canExtract, currentMeasureCode, refreshTask, showToast, taskId, validTaskId]);

  const handleLocate = useCallback(
    (label: string, text: string) => {
      const query = text.trim();
      if (!query) {
        showToast({
          title: "No evidence text",
          description: `${label} does not have source text to locate.`,
          tone: "info",
        });
        return;
      }

      setLocateTarget({ id: Date.now() + Math.random(), query, label });
    },
    [showToast],
  );

  const handleLocateResult = useCallback(
    async (result: { found: boolean; label: string }) => {
      if (result.found) {
        showToast({
          title: `${result.label} located`,
          description: "The source page is highlighted in the PDF viewer.",
          tone: "success",
        });
        return;
      }

      const fallbackText = locateTarget?.query.trim();
      if (!fallbackText) {
        showToast({
          title: "Source not found",
          description: "No matching PDF text was found for this evidence.",
          tone: "info",
        });
        return;
      }

      try {
        await navigator.clipboard.writeText(fallbackText);
        showToast({
          title: "Source not found",
          description: "The evidence text was copied so you can search manually.",
          tone: "info",
        });
      } catch {
        showToast({
          title: "Source not found",
          description: "No matching PDF text was found for this evidence.",
          tone: "info",
        });
      }
    },
    [locateTarget, showToast],
  );

  const handleConfirm = useCallback(async () => {
    if (!validTaskId || isConfirmed || !currentMeasureCode) {
      return;
    }

    try {
      setConfirming(true);
      const nssdPayload = buildNssdPayload(nssdDraft);
      const payload = {
        reviewer_conclusion: {
          decision: reviewerDecision,
          measure_code: currentMeasureCode,
          note: reviewerNote.trim(),
          selected_snippet: selectedEvidence?.snippet ?? "",
          nssd_form: nssdPayload,
        },
        nssd_payload: nssdPayload,
        is_confirmed: true,
      };
      const confirmResult = await confirmTask(taskId, payload);
      await refreshTask();
      setError(null);

      const autoClosedCodes = Array.from(
        new Set(
          confirmResult.linked_closed_measures
            .filter((item) => item.was_auto_closed)
            .map((item) => item.measure_code),
        ),
      );

      if (autoClosedCodes.length > 0) {
        showToast({
          title: "Success: Task closed",
          description: `Linked measures [${autoClosedCodes.join(", ")}] for this patient have also been automatically closed.`,
          tone: "success",
        });
      } else {
        showToast({
          title: `${currentMeasureCode} review confirmed`,
          description: "Reviewer conclusion and NSSD draft context were saved for audit traceability.",
          tone: "success",
        });
      }
    } catch (confirmError) {
      const message = confirmError instanceof Error ? confirmError.message : "Confirm request failed";
      setError(message);
      showToast({
        title: "Confirmation failed",
        description: message,
        tone: "error",
      });
    } finally {
      setConfirming(false);
    }
  }, [
    currentMeasureCode,
    isConfirmed,
    nssdDraft,
    refreshTask,
    reviewerDecision,
    reviewerNote,
    selectedEvidence,
    showToast,
    taskId,
    validTaskId,
  ]);

  const handleDraftChange = useCallback((field: keyof NssdDraft, value: string) => {
    setDraftOverrides((current) => ({ ...current, [field]: value }));
  }, []);

  return {
    taskDetail,
    status,
    loading,
    extracting,
    confirming,
    error,
    locateTarget,
    currentMeasureCode,
    selectedEvidence,
    readingEvidenceText,
    encounterEvidenceText,
    dosEvidenceText,
    showReviewContent,
    suggestionMeasureLabel,
    suggestionStatusLabel,
    suggestionStatusTone,
    suggestionSummaryText,
    agentTraceSteps,
    agentFinalSummary,
    liveAgentStep,
    historyOpen,
    conclusionHistory,
    nssdDraft,
    reviewerDecision,
    reviewerNote,
    isConfirmed,
    canExtract,
    handleExtract,
    handleLocate,
    handleLocateResult,
    handleConfirm,
    handleDraftChange,
    setLocateTarget,
    setHistoryOpen,
    setReviewerDecision,
    setReviewerNote,
  };
}
