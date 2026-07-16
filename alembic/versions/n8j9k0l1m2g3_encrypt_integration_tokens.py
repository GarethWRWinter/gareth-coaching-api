"""Widen integration-token columns to TEXT for encryption at rest.

Fernet ciphertext is longer than the plaintext token, so the Strava and
TrainingPeaks token columns (previously VARCHAR(255)) move to TEXT. Dropbox
is already TEXT. This migration only changes the column type; the actual
encryption of existing rows is done by scripts/encrypt_integration_tokens.py
(idempotent, run after TOKEN_ENCRYPTION_KEY is set) — kept out of the deploy
path so a missing key can never block a release.

Revision ID: n8j9k0l1m2g3
Revises: m7i8j9k0l1f2
Create Date: 2026-07-16
"""
from alembic import op
import sqlalchemy as sa

revision = "n8j9k0l1m2g3"
down_revision = "m7i8j9k0l1f2"
branch_labels = None
depends_on = None

_COLS = [
    ("strava_tokens", "access_token"),
    ("strava_tokens", "refresh_token"),
    ("trainingpeaks_tokens", "access_token"),
    ("trainingpeaks_tokens", "refresh_token"),
]


def upgrade() -> None:
    for table, col in _COLS:
        op.alter_column(table, col, type_=sa.Text(), existing_nullable=False)


def downgrade() -> None:
    for table, col in _COLS:
        op.alter_column(table, col, type_=sa.String(length=255), existing_nullable=False)
