from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import Column, DateTime, Enum as SAEnum, String, func
from sqlmodel import Field, SQLModel


class MeasureCode(str, Enum):
    CBP = "CBP"
    BPD = "BPD"
    GSD = "GSD"


class Measure(SQLModel, table=True):
    __tablename__ = "measures"

    id: Optional[int] = Field(default=None, primary_key=True)
    code: MeasureCode = Field(sa_column=Column(SAEnum(MeasureCode, name="measure_code"), unique=True, nullable=False))
    name: str = Field(sa_column=Column(String(128), nullable=False))
    description: Optional[str] = Field(default=None, sa_column=Column(String(512), nullable=True))
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False),
    )
