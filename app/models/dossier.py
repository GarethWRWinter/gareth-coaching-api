"""The Rider Dossier — the typed layer of what Forma knows about the rider.

Each entry is one learned fact on one dimension (fuel, time reality,
what lights them up...), with confidence and provenance. The dossier is
EARNED through conversation, never collected as a form: extraction adds
entries as the rider reveals them, and the gaps drive the coach's
one-question-at-a-time curiosity.
"""

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, generate_uuid

# dimension -> what it captures (used in prompts and gap detection).
# Ordered roughly by how early a coach would want to know it.
DOSSIER_DIMENSIONS: dict[str, str] = {
    "heartset": "the goal behind the goal — why they ride, what this season means",
    "time_reality": "hours they can genuinely train per week, and when",
    "time_aspiration": "hours they wish they had — the gap tells you their appetite",
    "logistics": "practical life: job pattern, family, travel, where they ride",
    "lights_up": "what makes riding feel great for them — climbs, speed, data, company",
    "frustrates": "what grinds them down — trainer boredom, weather, plateaus",
    "fuel_likes": "food they enjoy, on and off the bike",
    "fuel_dislikes": "food they despise or can't stomach mid-ride",
    "hydration": "drinking habits and problems",
    "recovery_habits": "sleep, rest-day behaviour, how they actually recover",
    "mindset": "confidence patterns, self-talk, how they respond to setbacks",
    "competing": "relationship with racing — nerves, tactics, ambition",
    "health_flags": "injuries, niggles, medical context that shapes training",
    "life_context": "current life events that bend the plan — work crunch, family",
}


class DossierEntry(Base):
    __tablename__ = "dossier_entries"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), index=True, nullable=False
    )
    dimension: Mapped[str] = mapped_column(String(40), index=True, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, server_default="0.6")
    # Where this was learned: "chat:<session_id>", "debrief:<ride_id>", "onboarding"
    source: Mapped[str | None] = mapped_column(String(255), nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    created_at: Mapped[str] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[str | None] = mapped_column(DateTime, onupdate=func.now(), nullable=True)
