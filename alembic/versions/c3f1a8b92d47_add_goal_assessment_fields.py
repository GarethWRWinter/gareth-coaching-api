"""add goal assessment fields (status, ride link, results, self-assessment)

Revision ID: c3f1a8b92d47
Revises: a2c9e4f71b83
Create Date: 2026-03-24 10:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'c3f1a8b92d47'
down_revision: Union[str, Sequence[str], None] = 'a2c9e4f71b83'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create goalstatus enum type
    goalstatus = sa.Enum('upcoming', 'completed', 'dnf', 'dns', name='goalstatus')
    goalstatus.create(op.get_bind(), checkfirst=True)

    # Add assessment columns to goal_events
    op.add_column('goal_events', sa.Column('status', sa.Enum('upcoming', 'completed', 'dnf', 'dns', name='goalstatus'), server_default='upcoming', nullable=True))
    op.add_column('goal_events', sa.Column('actual_ride_id', sa.String(36), sa.ForeignKey('rides.id'), nullable=True))
    op.add_column('goal_events', sa.Column('finish_time_seconds', sa.Integer(), nullable=True))
    op.add_column('goal_events', sa.Column('finish_position', sa.Integer(), nullable=True))
    op.add_column('goal_events', sa.Column('finish_position_total', sa.Integer(), nullable=True))
    op.add_column('goal_events', sa.Column('overall_satisfaction', sa.Integer(), nullable=True))
    op.add_column('goal_events', sa.Column('perceived_exertion', sa.Integer(), nullable=True))
    op.add_column('goal_events', sa.Column('assessment_data', sa.JSON(), nullable=True))
    op.add_column('goal_events', sa.Column('assessment_completed_at', sa.DateTime(), nullable=True))

    # Set all existing rows to 'upcoming'
    op.execute("UPDATE goal_events SET status = 'upcoming' WHERE status IS NULL")


def downgrade() -> None:
    op.drop_column('goal_events', 'assessment_completed_at')
    op.drop_column('goal_events', 'assessment_data')
    op.drop_column('goal_events', 'perceived_exertion')
    op.drop_column('goal_events', 'overall_satisfaction')
    op.drop_column('goal_events', 'finish_position_total')
    op.drop_column('goal_events', 'finish_position')
    op.drop_column('goal_events', 'finish_time_seconds')
    op.drop_column('goal_events', 'actual_ride_id')
    op.drop_column('goal_events', 'status')

    sa.Enum(name='goalstatus').drop(op.get_bind(), checkfirst=True)
