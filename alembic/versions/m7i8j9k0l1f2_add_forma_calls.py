"""forma_calls — cost/observability ledger for every Claude call (forma-core).

Revision ID: m7i8j9k0l1f2
Revises: l6h7i8j9k0e1
Create Date: 2026-07-16
"""
from alembic import op
import sqlalchemy as sa

revision = "m7i8j9k0l1f2"
down_revision = "l6h7i8j9k0e1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "forma_calls",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("ts", sa.DateTime(), nullable=False),
        sa.Column("task", sa.String(), nullable=False),
        sa.Column("surface", sa.String(), nullable=True),
        sa.Column("model", sa.String(), nullable=False),
        sa.Column("input_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("output_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("cache_read_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("cache_write_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("cost_cents", sa.Float(), nullable=False, server_default="0"),
        sa.Column("latency_ms", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.create_index("ix_forma_calls_user_id", "forma_calls", ["user_id"])
    op.create_index("ix_forma_calls_ts", "forma_calls", ["ts"])


def downgrade() -> None:
    op.drop_index("ix_forma_calls_ts", table_name="forma_calls")
    op.drop_index("ix_forma_calls_user_id", table_name="forma_calls")
    op.drop_table("forma_calls")
