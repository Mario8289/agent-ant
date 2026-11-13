"""extraction retry state on raw_events (issue #34)

Revision ID: 0008
Revises: 0007
Create Date: 2026-11-13
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0008"
down_revision: str | None = "0007"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Existing rows (voice calls and replies alike) start with zero attempts and no status.
    op.add_column(
        "raw_events",
        sa.Column("extraction_attempts", sa.Integer(), server_default="0", nullable=False),
    )
    op.add_column("raw_events", sa.Column("extraction_status", sa.Text(), nullable=True))
    op.create_check_constraint(
        op.f("ck_raw_events_extraction_status_valid"),
        "raw_events",
        "extraction_status IN ('done', 'failed', 'dead')",
    )


def downgrade() -> None:
    op.drop_constraint(
        op.f("ck_raw_events_extraction_status_valid"), "raw_events", type_="check"
    )
    op.drop_column("raw_events", "extraction_status")
    op.drop_column("raw_events", "extraction_attempts")