"""add workout execution assessment fields

Revision ID: h2c3d4e5f6a7
Revises: g1a2b3c4d5e6
Create Date: 2026-04-11 10:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'h2c3d4e5f6a7'
down_revision: Union[str, Sequence[str], None] = 'g1a2b3c4d5e6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'workouts',
        sa.Column('execution_score', sa.Float(), nullable=True),
    )
    op.add_column(
        'workouts',
        sa.Column('execution_feedback', sa.Text(), nullable=True),
    )
    op.add_column(
        'workouts',
        sa.Column('execution_adjustments', sa.JSON(), nullable=True),
    )
    op.add_column(
        'workouts',
        sa.Column('execution_assessed_at', sa.DateTime(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column('workouts', 'execution_assessed_at')
    op.drop_column('workouts', 'execution_adjustments')
    op.drop_column('workouts', 'execution_feedback')
    op.drop_column('workouts', 'execution_score')
