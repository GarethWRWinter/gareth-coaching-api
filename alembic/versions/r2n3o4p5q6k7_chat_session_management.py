"""Chat session management: pinned / starred / archived_at.

Revision ID: r2n3o4p5q6k7
Revises: q1m2n3o4p5j6
"""

import sqlalchemy as sa
from alembic import op

revision = "r2n3o4p5q6k7"
down_revision = "q1m2n3o4p5j6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "chat_sessions",
        sa.Column("pinned", sa.Boolean(), nullable=False, server_default="false"),
    )
    op.add_column(
        "chat_sessions",
        sa.Column("starred", sa.Boolean(), nullable=False, server_default="false"),
    )
    op.add_column(
        "chat_sessions",
        sa.Column("archived_at", sa.DateTime(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("chat_sessions", "archived_at")
    op.drop_column("chat_sessions", "starred")
    op.drop_column("chat_sessions", "pinned")
