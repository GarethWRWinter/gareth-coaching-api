"""add segments and achievements

Revision ID: f6b4c2d93e51
Revises: e5a3b7c91d20
Create Date: 2026-03-30 12:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers
revision: str = "f6b4c2d93e51"
down_revision: Union[str, None] = "e5a3b7c91d20"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Strava segments table
    op.create_table(
        "strava_segments",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("strava_segment_id", sa.BigInteger, unique=True, nullable=False, index=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("distance_meters", sa.Float, nullable=True),
        sa.Column("average_grade", sa.Float, nullable=True),
        sa.Column("climb_category", sa.Integer, nullable=True),
        sa.Column("city", sa.String(100), nullable=True),
        sa.Column("state", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )

    # Segment efforts table
    op.create_table(
        "segment_efforts",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("ride_id", sa.String(36), sa.ForeignKey("rides.id"), nullable=False, index=True),
        sa.Column("segment_id", sa.String(36), sa.ForeignKey("strava_segments.id"), nullable=False),
        sa.Column("strava_effort_id", sa.BigInteger, unique=True, nullable=True),
        sa.Column("elapsed_time_seconds", sa.Integer, nullable=False),
        sa.Column("moving_time_seconds", sa.Integer, nullable=True),
        sa.Column("average_watts", sa.Float, nullable=True),
        sa.Column("max_watts", sa.Integer, nullable=True),
        sa.Column("average_hr", sa.Float, nullable=True),
        sa.Column("max_hr", sa.Integer, nullable=True),
        sa.Column("pr_rank", sa.Integer, nullable=True),
        sa.Column("kom_rank", sa.Integer, nullable=True),
        sa.Column("achievement_type", sa.String(20), nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )
    op.create_index(
        "ix_segment_efforts_ride_segment",
        "segment_efforts",
        ["ride_id", "segment_id"],
    )

    # Add achievement/social columns to rides
    op.add_column("rides", sa.Column("achievement_count", sa.Integer, nullable=True))
    op.add_column("rides", sa.Column("pr_count", sa.Integer, nullable=True))
    op.add_column("rides", sa.Column("kudos_count", sa.Integer, nullable=True))


def downgrade() -> None:
    op.drop_column("rides", "kudos_count")
    op.drop_column("rides", "pr_count")
    op.drop_column("rides", "achievement_count")
    op.drop_index("ix_segment_efforts_ride_segment", table_name="segment_efforts")
    op.drop_table("segment_efforts")
    op.drop_table("strava_segments")
