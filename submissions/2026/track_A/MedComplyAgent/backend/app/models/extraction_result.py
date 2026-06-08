from datetime import datetime
from enum import Enum
from typing import Any, Optional

from sqlalchemy import Boolean, Column, DateTime, Enum as SAEnum, ForeignKey, Index, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel


class ExtractionStatus(str, Enum):
    PENDING = "PENDING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"


class ExtractionResult(SQLModel, table=True):
    __tablename__ = "extraction_results"
    __table_args__ = (Index("ix_extraction_patient_document", "patient_id", "document_id"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    patient_id: int = Field(sa_column=Column(ForeignKey("patients.id", ondelete="CASCADE"), index=True, nullable=False))
    document_id: int = Field(sa_column=Column(ForeignKey("documents.id", ondelete="CASCADE"), index=True, nullable=False))
    status: ExtractionStatus = Field(
        sa_column=Column(SAEnum(ExtractionStatus, name="extraction_status"), nullable=False)
    )
    extracted_payload: dict[str, Any] = Field(sa_column=Column(JSONB, nullable=False))
    model_name: Optional[str] = Field(default=None, sa_column=Column(String(128), nullable=True))
    is_valid: bool = Field(default=True, sa_column=Column(Boolean, nullable=False, server_default="true"))
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False),
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False),
    )
