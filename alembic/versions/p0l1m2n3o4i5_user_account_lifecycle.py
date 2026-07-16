"""users.is_active + users.deleted_at — account lifecycle for suspension + GDPR erasure.

Revision ID: p0l1m2n3o4i5
Revises: o9k0l1m2n3h4
Create Date: 2026-07-16
"""
from alembic import op
import sqlalchemy as sa

revision = "p0l1m2n3o4i5"
down_revision = "o9k0l1m2n3h4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.add_column("users", sa.Column("deleted_at", sa.DateTime(), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "deleted_at")
    op.drop_column("users", "is_active")
