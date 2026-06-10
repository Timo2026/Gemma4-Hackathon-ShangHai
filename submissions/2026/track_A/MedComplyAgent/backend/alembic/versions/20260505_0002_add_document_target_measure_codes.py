"""add document target measure codes

Revision ID: 20260505_0002
Revises: 20260501_0001
Create Date: 2026-05-05 00:00:00
"""

from alembic import op
import sqlalchemy as sa

revision = "20260505_0002"
down_revision = "20260501_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("documents", sa.Column("target_measure_codes", sa.String(length=64), nullable=True))


def downgrade() -> None:
    op.drop_column("documents", "target_measure_codes")
