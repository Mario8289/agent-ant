"""baseline: raw_events

Revision ID: 0001
Revises:
Create Date: 2026-11-07 21:52:41.503005
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "raw_events",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("idempotency_key", sa.Text(), nullable=False),
        sa.Column("source", sa.Text(), nullable=False),
        sa.Column("caller_number", sa.Text(), nullable=False),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "source IN ('voice_call', 'sms_reply')", name=op.f("ck_raw_events_source_valid")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_raw_events")),
        sa.UniqueConstraint("idempotency_key", name=op.f("uq_raw_events_idempotency_key")),
    )


def downgrade() -> None:
    op.drop_table("raw_events")
