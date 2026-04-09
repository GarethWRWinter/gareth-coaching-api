from sqlalchemy import BigInteger, Float, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, generate_uuid


class StravaSegment(TimestampMixin, Base):
    """Cached Strava segment metadata."""

    __tablename__ = "strava_segments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    strava_segment_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    distance_meters: Mapped[float | None] = mapped_column(Float, nullable=True)
    average_grade: Mapped[float | None] = mapped_column(Float, nullable=True)
    climb_category: Mapped[int | None] = mapped_column(Integer, nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    state: Mapped[str | None] = mapped_column(String(100), nullable=True)

    efforts = relationship("SegmentEffort", back_populates="segment")


class SegmentEffort(TimestampMixin, Base):
    """One segment effort per ride — links a ride to a Strava segment."""

    __tablename__ = "segment_efforts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    ride_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("rides.id"), index=True, nullable=False
    )
    segment_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("strava_segments.id"), nullable=False
    )
    strava_effort_id: Mapped[int | None] = mapped_column(BigInteger, unique=True, nullable=True)

    elapsed_time_seconds: Mapped[int] = mapped_column(Integer, nullable=False)
    moving_time_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)

    average_watts: Mapped[float | None] = mapped_column(Float, nullable=True)
    max_watts: Mapped[int | None] = mapped_column(Integer, nullable=True)
    average_hr: Mapped[float | None] = mapped_column(Float, nullable=True)
    max_hr: Mapped[int | None] = mapped_column(Integer, nullable=True)

    pr_rank: Mapped[int | None] = mapped_column(Integer, nullable=True)
    kom_rank: Mapped[int | None] = mapped_column(Integer, nullable=True)
    achievement_type: Mapped[str | None] = mapped_column(String(20), nullable=True)

    ride = relationship("Ride", back_populates="segment_efforts")
    segment = relationship("StravaSegment", back_populates="efforts")

    __table_args__ = (
        Index("ix_segment_efforts_ride_segment", "ride_id", "segment_id"),
    )
