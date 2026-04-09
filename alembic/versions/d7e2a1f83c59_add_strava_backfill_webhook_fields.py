"""add strava backfill and webhook tracking fields

Revision ID: d7e2a1f83c59
Revises: c3f1a8b92d47
Create Date: 2026-03-27 10:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers
revision: str = "d7e2a1f83c59"
down_revision: Union[str, None] = "c3f1a8b92d47"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("strava_tokens", sa.Column("backfill_status", sa.String(20), nullable=True))
    op.add_column("strava_tokens", sa.Column("backfill_total", sa.Integer(), nullable=True))
    op.add_column("strava_tokens", sa.Column("backfill_progress", sa.Integer(), nullable=True, server_default="0"))
    op.add_column("strava_tokens", sa.Column("backfill_started_at", sa.DateTime(), nullable=True))
    op.add_column("strava_tokens", sa.Column("backfill_completed_at", sa.DateTime(), nullable=True))
    op.add_column("strava_tokens", sa.Column("webhook_active", sa.Boolean(), nullable=False, server_default="false"))


def downgrade() -> None:
    op.drop_column("strava_tokens", "webhook_active")
    op.drop_column("strava_tokens", "backfill_completed_at")
    op.drop_column("strava_tokens", "backfill_started_at")
    op.drop_column("strava_tokens", "backfill_progress")
    op.drop_column("strava_tokens", "backfill_total")
    op.drop_column("strava_tokens", "backfill_status")
