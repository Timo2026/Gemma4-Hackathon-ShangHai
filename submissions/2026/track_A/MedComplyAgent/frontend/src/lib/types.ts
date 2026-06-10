export type JsonObject = Record<string, unknown>;

export type TaskStatus = "PENDING" | "EXTRACTED" | "CONFIRMED";

export interface TaskSummary {
  task_id: number;
  patient_id: number;
  patient_name: string;
  source_pdf_path: string;
  source_txt_path: string;
  status: TaskStatus | string;
  gap_status: string | null;
  measures: string[];
}

export interface ReviewerConclusionHistoryItem {
  measure_evaluation_id: number;
  task_id: number;
  patient_id: number;
  measure_code: string;
  decision: string;
  note: string;
  result_value: string;
  dos: string;
  patient_name: string;
  dob: string;
  confirmed_at: string | null;
  created_at: string | null;
  is_current_active_status: boolean;
}

export interface TaskDetail extends TaskSummary {
  latest_extraction: JsonObject | null;
  latest_evaluation: JsonObject | null;
  review_state?: ReviewState | null;
  reviewer_conclusion_history?: ReviewerConclusionHistoryItem[];
}

export interface SystemEvaluatedResult {
  measure_code: string;
  pass_flag: boolean;
  evidence_payload: JsonObject;
  measure_evaluation_id?: number;
}

export interface ReviewState {
  current_measure_code: string | null;
  current_evaluation: SystemEvaluatedResult | null;
  extraction_payload: JsonObject | null;
  is_suggested: boolean;
  is_confirmed: boolean;
  reviewer_conclusion: JsonObject | null;
  nssd_payload: JsonObject | null;
}

export interface ExtractResponse {
  task_id: number;
  extraction_result_id: number;
  measure_evaluation_id: number;
  raw_extraction: JsonObject;
  system_evaluated_result: SystemEvaluatedResult;
  measure_evaluation_ids: number[];
  system_evaluated_results: SystemEvaluatedResult[];
}

export interface NssdPayload {
  patient_name: string;
  dob: string;
  result_value: string;
  dos: string;
  rendering_provider: string;
  place_of_service: string;
  encounter_type: string;
}

export interface NssdCandidate extends NssdPayload {
  evidence_id: string;
  measure_hint: string;
  snippet: string;
  encounter_snippet: string;
  date_snippet: string;
}

export interface ConfirmRequest {
  reviewer_conclusion: JsonObject;
  nssd_payload?: NssdPayload;
  is_confirmed: boolean;
}

export interface LinkedClosedMeasureItem {
  measure_evaluation_id: number;
  measure_code: string;
  was_auto_closed: boolean;
}

export interface ConfirmResponse {
  task_id: number;
  status: TaskStatus | string;
  measure_evaluation_id: number;
  reviewer_conclusion: JsonObject;
  evidence_payload: JsonObject;
  linked_closed_measures: LinkedClosedMeasureItem[];
}
