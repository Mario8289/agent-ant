"""job_status and job_events (D-030, issue #124)

Revision ID: 0010
Revises: 0009
Create Date: 2026-11-22
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0010"
down_revision: str | None = "0009"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Job progress is its own column, separate from the extraction-review ``status``. Every
    # existing job is a lead, so it starts at ``enquiry`` (D-030).
    op.add_column(
        "job_records",
        sa.Column("job_status", sa.Text(), server_default="enquiry", nullable=False),
    )
    op.add_column(
        "job_records",
        sa.Column("on_hold", sa.Boolean(), server_default=sa.text("false"), nullable=False),
    )
    op.create_check_constraint(
        op.f("ck_job_records_job_status_valid"),
        "job_records",
        "job_status IN ('enquiry', 'in_progress', 'completed', 'lost')",
    )

    # Append-only history of every status move (D-030). The first state a job enters is recorded
    # on the job row itself (``job_status`` + ``created_at``), so transitions are the only rows.
    op.create_table(
        "job_events",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("job_id", sa.BigInteger(), nullable=False),
        sa.Column("from_status", sa.Text(), nullable=False),
        sa.Column("to_status", sa.Text(), nullable=False),
        sa.Column("actor", sa.Text(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["job_id"],
            ["job_records.id"],
            name=op.f("fk_job_events_job_id_job_records"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_job_events")),
    )


def downgrade() -> None:
    op.drop_table("job_events")
    op.drop_constraint(
        op.f("ck_job_records_job_status_valid"), "job_records", type_="check"
    )
    op.drop_column("job_records", "on_hold")
    op.drop_column("job_records", "job_status")
