"""Add coach personalisation: name, avatar, tone

Revision ID: k5g6h7i8j9d0
Revises: j4f5g6h7i8c9
Create Date: 2026-07-03
"""
from alembic import op
import sqlalchemy as sa

revision = "k5g6h7i8j9d0"
down_revision = "j4f5g6h7i8c9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("coach_name", sa.String(50), nullable=False, server_default="Marco"))
    op.add_column("users", sa.Column("coach_avatar", sa.String(32), nullable=False, server_default="m1_climber"))
    op.add_column("users", sa.Column("coach_tone", sa.String(24), nullable=False, server_default="balanced"))


def downgrade() -> None:
    op.drop_column("users", "coach_tone")
    op.drop_column("users", "coach_avatar")
    op.drop_column("users", "coach_name")
