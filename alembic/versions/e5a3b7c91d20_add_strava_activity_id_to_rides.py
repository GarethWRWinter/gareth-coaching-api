"""add strava_activity_id to rides

Revision ID: e5a3b7c91d20
Revises: d7e2a1f83c59
Create Date: 2026-03-28 12:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers
revision: str = "e5a3b7c91d20"
down_revision: Union[str, None] = "d7e2a1f83c59"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "rides",
        sa.Column("strava_activity_id", sa.String(100), nullable=True),
    )
    op.create_index(
        "ix_rides_strava_activity_id", "rides", ["strava_activity_id"]
    )


def downgrade() -> None:
    op.drop_index("ix_rides_strava_activity_id", table_name="rides")
    op.drop_column("rides", "strava_activity_id")
