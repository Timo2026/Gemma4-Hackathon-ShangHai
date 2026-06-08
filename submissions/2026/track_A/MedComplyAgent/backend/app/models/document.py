from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, ForeignKey, String, func
from sqlmodel import Field, SQLModel


class Document(SQLModel, table=True):
    __tablename__ = "documents"

    id: Optional[int] = Field(default=None, primary_key=True)
    patient_id: int = Field(sa_column=Column(ForeignKey("patients.id", ondelete="CASCADE"), index=True, nullable=False))
    source_pdf_path: str = Field(sa_column=Column(String(512), nullable=False))
    source_txt_path: str = Field(sa_column=Column(String(512), nullable=False))
    target_measure_codes: Optional[str] = Field(default=None, sa_column=Column(String(64), nullable=True))
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False),
    )
