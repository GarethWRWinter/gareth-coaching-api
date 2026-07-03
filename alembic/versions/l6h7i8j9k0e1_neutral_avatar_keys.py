"""Neutralise coach avatar keys: descriptive keys → coach_01..coach_10

The rider decides what they see in each face — no archetype or demographic
context in customer-facing identifiers.

Revision ID: l6h7i8j9k0e1
Revises: k5g6h7i8j9d0
Create Date: 2026-07-03
"""
from alembic import op
import sqlalchemy as sa

revision = "l6h7i8j9k0e1"
down_revision = "k5g6h7i8j9d0"
branch_labels = None
depends_on = None

MAPPING = {
    "m1_climber": "coach_01",
    "m2_sprinter": "coach_02",
    "m3_tt": "coach_03",
    "m4_ds": "coach_04",
    "m5_allrounder": "coach_05",
    "f1_hardwoman": "coach_06",
    "f2_sprinter": "coach_07",
    "f3_climber": "coach_08",
    "f4_professor": "coach_09",
    "f5_endurance": "coach_10",
}


def upgrade() -> None:
    op.alter_column("users", "coach_avatar", server_default="coach_01")
    for old, new in MAPPING.items():
        op.execute(
            sa.text("UPDATE users SET coach_avatar = :new WHERE coach_avatar = :old")
            .bindparams(new=new, old=old)
        )


def downgrade() -> None:
    op.alter_column("users", "coach_avatar", server_default="m1_climber")
    for old, new in MAPPING.items():
        op.execute(
            sa.text("UPDATE users SET coach_avatar = :old WHERE coach_avatar = :new")
            .bindparams(new=new, old=old)
        )
