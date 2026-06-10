"""init schema

Revision ID: 20260501_0001
Revises:
Create Date: 2026-05-01 11:45:00
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260501_0001"
down_revision = None
branch_labels = None
depends_on = None


measure_code_enum = sa.Enum("CBP", "BPD", "GSD", name="measure_code")
extraction_status_enum = sa.Enum("PENDING", "SUCCEEDED", "FAILED", name="extraction_status")


def upgrade() -> None:
    op.create_table(
        "patients",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("member_id", sa.String(length=64), nullable=False),
        sa.Column("first_name", sa.String(length=128), nullable=False),
        sa.Column("last_name", sa.String(length=128), nullable=False),
        sa.Column("date_of_birth", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_patients_member_id", "patients", ["member_id"], unique=True)

    op.create_table(
        "measures",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", measure_code_enum, nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("description", sa.String(length=512), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code", name="uq_measures_code"),
    )

    op.create_table(
        "documents",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("patient_id", sa.Integer(), nullable=False),
        sa.Column("source_pdf_path", sa.String(length=512), nullable=False),
        sa.Column("source_txt_path", sa.String(length=512), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["patient_id"], ["patients.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_documents_patient_id", "documents", ["patient_id"], unique=False)

    op.create_table(
        "extraction_results",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("patient_id", sa.Integer(), nullable=False),
        sa.Column("document_id", sa.Integer(), nullable=False),
        sa.Column("status", extraction_status_enum, nullable=False),
        sa.Column("extracted_payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("model_name", sa.String(length=128), nullable=True),
        sa.Column("is_valid", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["patient_id"], ["patients.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_extraction_results_patient_id", "extraction_results", ["patient_id"], unique=False)
    op.create_index("ix_extraction_results_document_id", "extraction_results", ["document_id"], unique=False)
    op.create_index("ix_extraction_patient_document", "extraction_results", ["patient_id", "document_id"], unique=False)

    op.create_table(
        "measure_evaluations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("patient_id", sa.Integer(), nullable=False),
        sa.Column("measure_id", sa.Integer(), nullable=False),
        sa.Column("document_id", sa.Integer(), nullable=False),
        sa.Column("extraction_result_id", sa.Integer(), nullable=False),
        sa.Column("pass_flag", sa.Boolean(), nullable=False),
        sa.Column("evidence_payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["extraction_result_id"], ["extraction_results.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["measure_id"], ["measures.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["patient_id"], ["patients.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_measure_evaluations_patient_id", "measure_evaluations", ["patient_id"], unique=False)
    op.create_index("ix_measure_evaluations_measure_id", "measure_evaluations", ["measure_id"], unique=False)
    op.create_index("ix_measure_evaluations_document_id", "measure_evaluations", ["document_id"], unique=False)
    op.create_index("ix_measure_evaluations_extraction_result_id", "measure_evaluations", ["extraction_result_id"], unique=False)
    op.create_index("ix_eval_patient_measure_created", "measure_evaluations", ["patient_id", "measure_id", "created_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_eval_patient_measure_created", table_name="measure_evaluations")
    op.drop_index("ix_measure_evaluations_extraction_result_id", table_name="measure_evaluations")
    op.drop_index("ix_measure_evaluations_document_id", table_name="measure_evaluations")
    op.drop_index("ix_measure_evaluations_measure_id", table_name="measure_evaluations")
    op.drop_index("ix_measure_evaluations_patient_id", table_name="measure_evaluations")
    op.drop_table("measure_evaluations")

    op.drop_index("ix_extraction_patient_document", table_name="extraction_results")
    op.drop_index("ix_extraction_results_document_id", table_name="extraction_results")
    op.drop_index("ix_extraction_results_patient_id", table_name="extraction_results")
    op.drop_table("extraction_results")

    op.drop_index("ix_documents_patient_id", table_name="documents")
    op.drop_table("documents")

    op.drop_table("measures")
    op.drop_index("ix_patients_member_id", table_name="patients")
    op.drop_table("patients")

    extraction_status_enum.drop(op.get_bind(), checkfirst=True)
    measure_code_enum.drop(op.get_bind(), checkfirst=True)
