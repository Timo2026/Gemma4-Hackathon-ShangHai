from datetime import datetime
from typing import Any, Optional

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Index, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel


class MeasureEvaluation(SQLModel, table=True):
    __tablename__ = "measure_evaluations"
    __table_args__ = (Index("ix_eval_patient_measure_created", "patient_id", "measure_id", "created_at"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    patient_id: int = Field(sa_column=Column(ForeignKey("patients.id", ondelete="CASCADE"), index=True, nullable=False))
    measure_id: int = Field(sa_column=Column(ForeignKey("measures.id", ondelete="CASCADE"), index=True, nullable=False))
    document_id: int = Field(sa_column=Column(ForeignKey("documents.id", ondelete="CASCADE"), index=True, nullable=False))
    extraction_result_id: int = Field(
        sa_column=Column(ForeignKey("extraction_results.id", ondelete="CASCADE"), index=True, nullable=False)
    )
    pass_flag: bool = Field(sa_column=Column(Boolean, nullable=False))
    evidence_payload: dict[str, Any] = Field(sa_column=Column(JSONB, nullable=False))
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False),
    )
