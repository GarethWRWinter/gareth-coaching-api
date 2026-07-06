"""Memory graph — Forma's brain (Pillar 2, v2).

Typed entity graph: `mem_entities` are nodes (a Value, Goal, LearningGap,
Insight, Habit, LifeEvent, Person, HealthSignal, Procedural, RideMemory);
`mem_edges` are typed relationships between them (GROUNDS, SERVES, SURFACES,
ADDRESSED_BY, BECAME, INVOLVES, CONSTRAINS, ABOUT).

The relationships are where the intelligence lives — a plan, a coaching
narrative, or "Forma's reading of your brain" is a traversal, not a stored
blob. See prd/cycling-coach/memory-layer.md (v2).
"""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, generate_uuid


class MemoryEntity(Base):
    __tablename__ = "mem_entities"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), index=True, nullable=False
    )

    # Taxonomy: type is the noun; kind is the subtype tag (tags, not types).
    type: Mapped[str] = mapped_column(String(32), nullable=False)  # value|goal|gap|insight|habit|life_event|person|health_signal|procedural|ride_memory
    kind: Mapped[str | None] = mapped_column(String(48), nullable=True)
    life_area: Mapped[str] = mapped_column(String(16), nullable=False, default="training")  # training|body|mind|life

    label: Mapped[str] = mapped_column(String(255), nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    attrs: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Lifecycle + trust
    status: Mapped[str | None] = mapped_column(String(24), nullable=True)  # insights: noted|applied|became_habit|rejected
    visibility: Mapped[str] = mapped_column(String(16), nullable=False, default="private")
    hidden_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Provenance
    source: Mapped[str | None] = mapped_column(String(24), nullable=True)  # chat|debrief|onboarding|system
    source_ref: Mapped[str | None] = mapped_column(String(64), nullable=True)  # e.g. ride_id, session_id

    # Reserved for semantic retrieval (vendor TBD — memory-layer OQ1).
    embedding: Mapped[list | None] = mapped_column(JSONB, nullable=True)

    observed_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, onupdate=func.now(), nullable=True)

    user = relationship("User")

    __table_args__ = (
        Index("ix_mem_entities_user_type", "user_id", "type"),
    )


class MemoryEdge(Base):
    __tablename__ = "mem_edges"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), index=True, nullable=False
    )
    from_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("mem_entities.id", ondelete="CASCADE"), index=True, nullable=False
    )
    to_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("mem_entities.id", ondelete="CASCADE"), index=True, nullable=False
    )
    edge_type: Mapped[str] = mapped_column(String(24), nullable=False)  # grounds|serves|surfaces|addressed_by|became|involves|constrains|about
    attrs: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
