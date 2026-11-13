"""outbound SMS persistence (issue #73)

Revision ID: 0006
Revises: 0005
Create Date: 2026-11-13
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0006"
down_revision: str | None = "0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "outbound_messages",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("twilio_message_sid", sa.Text(), nullable=True),
        sa.Column("raw_event_id", sa.BigInteger(), nullable=False),
        sa.Column("to", sa.Text(), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("error_code", sa.Text(), nullable=True),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["raw_event_id"],
            ["raw_events.id"],
            name=op.f("fk_outbound_messages_raw_event_id_raw_events"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_outbound_messages")),
        sa.UniqueConstraint(
            "twilio_message_sid", name=op.f("uq_outbound_messages_twilio_message_sid")
        ),
    )


def downgrade() -> None:
    op.drop_table("outbound_messages")
