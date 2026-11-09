"""job records and the audit -> job link

Revision ID: 0004
Revises: 0003
Create Date: 2026-11-09
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0004"
down_revision: str | None = "0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "job_records",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("raw_event_id", sa.BigInteger(), nullable=False),
        sa.Column("idempotency_key", sa.Text(), nullable=False),
        sa.Column("caller_number", sa.Text(), nullable=False),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("raw_message", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=True),
        sa.Column("job_type", sa.Text(), nullable=True),
        sa.Column("location", sa.Text(), nullable=True),
        sa.Column("urgency", sa.Text(), nullable=False),
        sa.Column("preferred_date", sa.Text(), nullable=True),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("extraction_confidence", sa.Float(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "status IN ('captured', 'needs_review', 'approved', 'rejected')",
            name=op.f("ck_job_records_status_valid"),
        ),
        sa.CheckConstraint(
            "urgency IN ('low', 'medium', 'high', 'unknown')",
            name=op.f("ck_job_records_urgency_valid"),
        ),
        sa.ForeignKeyConstraint(
            ["raw_event_id"],
            ["raw_events.id"],
            name=op.f("fk_job_records_raw_event_id_raw_events"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_job_records")),
        sa.UniqueConstraint("idempotency_key", name=op.f("uq_job_records_idempotency_key")),
    )
    # The audit row's job_id was left without a foreign key until job_records existed (D-012).
    op.create_foreign_key(
        op.f("fk_llm_output_audits_job_id_job_records"),
        "llm_output_audits",
        "job_records",
        ["job_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        op.f("fk_llm_output_audits_job_id_job_records"), "llm_output_audits", type_="foreignkey"
    )
    op.drop_table("job_records")
