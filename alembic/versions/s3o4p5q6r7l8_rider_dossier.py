"""Rider Dossier: dossier_entries table.

Revision ID: s3o4p5q6r7l8
Revises: r2n3o4p5q6k7
"""

import sqlalchemy as sa
from alembic import op

revision = "s3o4p5q6r7l8"
down_revision = "r2n3o4p5q6k7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "dossier_entries",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "user_id",
            sa.String(36),
            sa.ForeignKey("users.id"),
            nullable=False,
            index=True,
        ),
        sa.Column("dimension", sa.String(40), nullable=False, index=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False, server_default="0.6"),
        sa.Column("source", sa.String(255), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("dossier_entries")
