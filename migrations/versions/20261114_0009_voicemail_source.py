"""voicemail source on raw_events (issue #33)

Revision ID: 0009
Revises: 0008
Create Date: 2026-11-14
"""

from collections.abc import Sequence

from alembic import op

revision: str = "0009"
down_revision: str | None = "0008"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_constraint(op.f("ck_raw_events_source_valid"), "raw_events", type_="check")
    op.create_check_constraint(
        op.f("ck_raw_events_source_valid"),
        "raw_events",
        "source IN ('voice_call', 'sms_reply', 'voicemail')",
    )


def downgrade() -> None:
    op.drop_constraint(op.f("ck_raw_events_source_valid"), "raw_events", type_="check")
    op.create_check_constraint(
        op.f("ck_raw_events_source_valid"),
        "raw_events",
        "source IN ('voice_call', 'sms_reply')",
    )