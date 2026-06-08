from datetime import date, datetime
from typing import Optional

from sqlalchemy import Column, DateTime, String, func
from sqlmodel import Field, SQLModel


class Patient(SQLModel, table=True):
    __tablename__ = "patients"

    id: Optional[int] = Field(default=None, primary_key=True)
    member_id: str = Field(sa_column=Column(String(64), unique=True, index=True, nullable=False))
    first_name: str = Field(sa_column=Column(String(128), nullable=False))
    last_name: str = Field(sa_column=Column(String(128), nullable=False))
    date_of_birth: Optional[date] = Field(default=None)
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False),
    )
