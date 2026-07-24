"""Cached time-in-zone summary on rides for list views.

Revision ID: t4p5q6r7s8m9
Revises: s3o4p5q6r7l8
"""

import sqlalchemy as sa
from alembic import op

revision = "t4p5q6r7s8m9"
down_revision = "s3o4p5q6r7l8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("rides", sa.Column("zone_summary", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("rides", "zone_summary")
