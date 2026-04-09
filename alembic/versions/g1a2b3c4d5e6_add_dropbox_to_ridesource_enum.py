"""add dropbox to ridesource enum

Revision ID: g1a2b3c4d5e6
Revises: c9ad7200de7c
Create Date: 2026-04-09 14:30:00.000000
"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "g1a2b3c4d5e6"
down_revision = "c9ad7200de7c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TYPE ridesource ADD VALUE IF NOT EXISTS 'dropbox'")


def downgrade() -> None:
    # PostgreSQL doesn't support removing enum values easily
    pass
