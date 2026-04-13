"""Add coach presence: ride debrief columns and coach_nudges table

Revision ID: i3d4e5f6g7b8
Revises: h2c3d4e5f6a7
Create Date: 2026-04-13
"""
from alembic import op
import sqlalchemy as sa

revision = "i3d4e5f6g7b8"
down_revision = "h2c3d4e5f6a7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add debrief columns to rides
    op.add_column("rides", sa.Column("debrief_text", sa.Text(), nullable=True))
    op.add_column("rides", sa.Column("debrief_generated_at", sa.DateTime(), nullable=True))

    # Create coach_nudges table
    op.create_table(
        "coach_nudges",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False, index=True),
        sa.Column("nudge_date", sa.Date(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("coach_nudges")
    op.drop_column("rides", "debrief_generated_at")
    op.drop_column("rides", "debrief_text")
