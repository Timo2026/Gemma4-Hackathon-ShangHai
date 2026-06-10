from typing import Any

from pydantic import BaseModel, Field


class TaskSummary(BaseModel):
    task_id: int
    patient_id: int
    patient_name: str
    source_pdf_path: str
    source_txt_path: str
    status: str
    gap_status: str | None = None
    measures: list[str] = []


class ReviewerConclusionHistoryItem(BaseModel):
    measure_evaluation_id: int
    task_id: int
    patient_id: int
    measure_code: str
    decision: str
    note: str
    result_value: str
    dos: str
    patient_name: str
    dob: str
    confirmed_at: str | None = None
    created_at: str | None = None
    is_current_active_status: bool = False


class TaskDetail(TaskSummary):
    latest_extraction: dict[str, Any] | None = None
    latest_evaluation: dict[str, Any] | None = None
    review_state: dict[str, Any] | None = None
    reviewer_conclusion_history: list[ReviewerConclusionHistoryItem] = []


class ExtractRequest(BaseModel):
    measure_ids: list[int] | None = None


class ExtractResponse(BaseModel):
    task_id: int
    extraction_result_id: int
    measure_evaluation_id: int
    raw_extraction: dict[str, Any]
    system_evaluated_result: dict[str, Any]
    measure_evaluation_ids: list[int]
    system_evaluated_results: list[dict[str, Any]]


class ConfirmRequest(BaseModel):
    reviewer_conclusion: dict[str, Any] = Field(default_factory=dict)
    nssd_payload: dict[str, Any] = Field(default_factory=dict)
    is_confirmed: bool = True


class LinkedClosedMeasureItem(BaseModel):
    measure_evaluation_id: int
    measure_code: str
    was_auto_closed: bool


class ConfirmResponse(BaseModel):
    task_id: int
    status: str
    measure_evaluation_id: int
    reviewer_conclusion: dict[str, Any]
    evidence_payload: dict[str, Any]
    linked_closed_measures: list[LinkedClosedMeasureItem] = []
