"""llm output audit and human edits

Revision ID: 0003
Revises: 0002
Create Date: 2026-11-09
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "llm_output_audits",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("raw_event_id", sa.BigInteger(), nullable=False),
        sa.Column("job_id", sa.BigInteger(), nullable=True),
        sa.Column("model", sa.Text(), nullable=False),
        sa.Column("prompt_version", sa.Text(), nullable=False),
        sa.Column("raw_output", sa.Text(), nullable=False),
        sa.Column("validated", sa.Boolean(), nullable=False),
        sa.Column("repair_attempts", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "repair_attempts >= 0",
            name=op.f("ck_llm_output_audits_repair_attempts_nonnegative"),
        ),
        sa.ForeignKeyConstraint(
            ["raw_event_id"],
            ["raw_events.id"],
            name=op.f("fk_llm_output_audits_raw_event_id_raw_events"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_llm_output_audits")),
    )
    op.create_table(
        "human_edits",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("llm_output_id", sa.BigInteger(), nullable=False),
        sa.Column("edit_diff", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["llm_output_id"],
            ["llm_output_audits.id"],
            name=op.f("fk_human_edits_llm_output_id_llm_output_audits"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_human_edits")),
    )


def downgrade() -> None:
    op.drop_table("human_edits")
    op.drop_table("llm_output_audits")
