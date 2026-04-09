from sqlalchemy import Date, Float, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, generate_uuid


class DailyMetrics(Base):
    __tablename__ = "daily_metrics"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), index=True, nullable=False
    )
    date: Mapped[str] = mapped_column(Date, nullable=False)
    tss: Mapped[float] = mapped_column(Float, default=0.0)
    ctl: Mapped[float] = mapped_column(Float, default=0.0)
    atl: Mapped[float] = mapped_column(Float, default=0.0)
    tsb: Mapped[float] = mapped_column(Float, default=0.0)
    ramp_rate: Mapped[float | None] = mapped_column(Float, nullable=True)

    user = relationship("User", back_populates="daily_metrics")

    __table_args__ = (
        UniqueConstraint("user_id", "date", name="uq_daily_metrics_user_date"),
    )
