"""opt-out state for HELP/STOP handling (#72)

Revision ID: 0005
Revises: 0004
Create Date: 2026-11-13
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0005"
down_revision: str | None = "0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "opt_outs",
        sa.Column("caller_number", sa.Text(), nullable=False),
        sa.Column(
            "opted_out_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("caller_number", name=op.f("pk_opt_outs")),
    )


def downgrade() -> None:
    op.drop_table("opt_outs")
