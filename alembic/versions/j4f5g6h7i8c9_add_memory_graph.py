"""Add memory graph: mem_entities + mem_edges (Pillar 2 v2 — the Brain)

Revision ID: j4f5g6h7i8c9
Revises: i3d4e5f6g7b8
Create Date: 2026-06-14
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision = "j4f5g6h7i8c9"
down_revision = "i3d4e5f6g7b8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "mem_entities",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False, index=True),
        sa.Column("type", sa.String(32), nullable=False),
        sa.Column("kind", sa.String(48), nullable=True),
        sa.Column("life_area", sa.String(16), nullable=False, server_default="training"),
        sa.Column("label", sa.String(255), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("attrs", JSONB(), nullable=True),
        sa.Column("status", sa.String(24), nullable=True),
        sa.Column("visibility", sa.String(16), nullable=False, server_default="private"),
        sa.Column("hidden_at", sa.DateTime(), nullable=True),
        sa.Column("source", sa.String(24), nullable=True),
        sa.Column("source_ref", sa.String(64), nullable=True),
        sa.Column("embedding", JSONB(), nullable=True),
        sa.Column("observed_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_mem_entities_user_type", "mem_entities", ["user_id", "type"])

    op.create_table(
        "mem_edges",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False, index=True),
        sa.Column("from_id", sa.String(36), sa.ForeignKey("mem_entities.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("to_id", sa.String(36), sa.ForeignKey("mem_entities.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("edge_type", sa.String(24), nullable=False),
        sa.Column("attrs", JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("mem_edges")
    op.drop_index("ix_mem_entities_user_type", table_name="mem_entities")
    op.drop_table("mem_entities")
