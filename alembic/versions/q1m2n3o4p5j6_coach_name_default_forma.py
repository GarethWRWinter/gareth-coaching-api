"""Fix coach_name server default: Marco -> Forma.

The k5g6h7i8j9d0 migration created users.coach_name with server_default
'Marco'. The model later moved to 'Forma' but the DB-level default was
never altered, so every user created since the rebrand got 'Marco'.
Alter the column default and re-run the backfill for rows created in
the gap.

Revision ID: q1m2n3o4p5j6
Revises: p0l1m2n3o4i5
"""

from alembic import op

revision = "q1m2n3o4p5j6"
down_revision = "p0l1m2n3o4i5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE users ALTER COLUMN coach_name SET DEFAULT 'Forma'")
    # Rows created while the stale default was live. Anyone who truly wants
    # their coach called Marco can rename in Settings; the brand default wins.
    op.execute("UPDATE users SET coach_name = 'Forma' WHERE coach_name = 'Marco'")


def downgrade() -> None:
    op.execute("ALTER TABLE users ALTER COLUMN coach_name SET DEFAULT 'Marco'")
