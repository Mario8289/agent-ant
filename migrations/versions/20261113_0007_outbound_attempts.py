"""outbound send attempt counter (issue #34)

Revision ID: 0007
Revises: 0006
Create Date: 2026-11-13
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0007"
down_revision: str | None = "0006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Every existing row has had one send attempt; new rows start at 1 too.
    op.add_column(
        "outbound_messages",
        sa.Column("attempts", sa.Integer(), server_default="1", nullable=False),
    )


def downgrade() -> None:
    op.drop_column("outbound_messages", "attempts")
