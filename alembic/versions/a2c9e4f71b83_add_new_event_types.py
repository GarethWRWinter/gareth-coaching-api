"""add new event types (hill_climb, stage_race, charity_ride, century)

Revision ID: a2c9e4f71b83
Revises: 8f88268ad474
Create Date: 2026-03-15 16:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'a2c9e4f71b83'
down_revision: Union[str, Sequence[str], None] = '8f88268ad474'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new values to the eventtype enum
    op.execute("ALTER TYPE eventtype ADD VALUE IF NOT EXISTS 'hill_climb'")
    op.execute("ALTER TYPE eventtype ADD VALUE IF NOT EXISTS 'stage_race'")
    op.execute("ALTER TYPE eventtype ADD VALUE IF NOT EXISTS 'charity_ride'")
    op.execute("ALTER TYPE eventtype ADD VALUE IF NOT EXISTS 'century'")


def downgrade() -> None:
    # PostgreSQL doesn't easily support removing enum values
    # This is intentionally a no-op for safety
    pass
