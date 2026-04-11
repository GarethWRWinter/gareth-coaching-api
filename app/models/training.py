import enum

from sqlalchemy import JSON, Date, DateTime, Enum, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, generate_uuid


class PlanStatus(str, enum.Enum):
    draft = "draft"
    active = "active"
    completed = "completed"
    cancelled = "cancelled"


class PeriodizationModel(str, enum.Enum):
    traditional = "traditional"
    polarized = "polarized"
    sweet_spot = "sweet_spot"


class PhaseType(str, enum.Enum):
    off_season = "off_season"
    base = "base"
    build = "build"
    peak = "peak"
    race = "race"
    recovery = "recovery"


class WorkoutType(str, enum.Enum):
    endurance = "endurance"
    tempo = "tempo"
    sweet_spot = "sweet_spot"
    threshold = "threshold"
    vo2max = "vo2max"
    sprint = "sprint"
    recovery = "recovery"
    rest = "rest"


class WorkoutStatus(str, enum.Enum):
    planned = "planned"
    completed = "completed"
    skipped = "skipped"
    modified = "modified"


class StepType(str, enum.Enum):
    warmup = "warmup"
    steady_state = "steady_state"
    interval_on = "interval_on"
    interval_off = "interval_off"
    cooldown = "cooldown"
    free_ride = "free_ride"
    ramp = "ramp"


class TrainingPlan(Base):
    __tablename__ = "training_plans"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    goal_event_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("goal_events.id"), nullable=True
    )
    start_date: Mapped[str] = mapped_column(Date, nullable=False)
    end_date: Mapped[str] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(Enum(PlanStatus), default=PlanStatus.draft)
    periodization_model: Mapped[str] = mapped_column(
        Enum(PeriodizationModel), default=PeriodizationModel.traditional
    )
    created_at: Mapped[str] = mapped_column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="training_plans")
    goal_event = relationship("GoalEvent")
    phases = relationship(
        "TrainingPhase", back_populates="plan", cascade="all, delete-orphan",
        order_by="TrainingPhase.sort_order"
    )


class TrainingPhase(Base):
    __tablename__ = "training_phases"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    plan_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("training_plans.id"), nullable=False
    )
    phase_type: Mapped[str] = mapped_column(Enum(PhaseType), nullable=False)
    start_date: Mapped[str] = mapped_column(Date, nullable=False)
    end_date: Mapped[str] = mapped_column(Date, nullable=False)
    target_weekly_tss: Mapped[float | None] = mapped_column(Float, nullable=True)
    target_weekly_hours: Mapped[float | None] = mapped_column(Float, nullable=True)
    focus: Mapped[str | None] = mapped_column(String(255), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    plan = relationship("TrainingPlan", back_populates="phases")
    workouts = relationship(
        "Workout", back_populates="phase", cascade="all, delete-orphan",
        order_by="Workout.scheduled_date"
    )


class Workout(Base):
    __tablename__ = "workouts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    phase_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("training_phases.id"), nullable=True
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), index=True, nullable=False
    )
    scheduled_date: Mapped[str] = mapped_column(Date, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    workout_type: Mapped[str] = mapped_column(Enum(WorkoutType), nullable=False)
    planned_duration_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    planned_tss: Mapped[float | None] = mapped_column(Float, nullable=True)
    planned_if: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(Enum(WorkoutStatus), default=WorkoutStatus.planned)
    actual_ride_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("rides.id"), nullable=True
    )
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    # Post-ride execution assessment — lazily generated the first time the
    # linked ride is viewed, cached until the user re-runs it.
    execution_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    execution_feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    execution_adjustments: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    execution_assessed_at: Mapped[str | None] = mapped_column(DateTime, nullable=True)

    phase = relationship("TrainingPhase", back_populates="workouts")
    user = relationship("User", back_populates="workouts")
    actual_ride = relationship("Ride", foreign_keys=[actual_ride_id])
    steps = relationship(
        "WorkoutStep", back_populates="workout", cascade="all, delete-orphan",
        order_by="WorkoutStep.step_order"
    )


class WorkoutStep(Base):
    __tablename__ = "workout_steps"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    workout_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("workouts.id"), nullable=False
    )
    step_order: Mapped[int] = mapped_column(Integer, nullable=False)
    step_type: Mapped[str] = mapped_column(Enum(StepType), nullable=False)
    duration_seconds: Mapped[int] = mapped_column(Integer, nullable=False)
    power_target_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    power_low_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    power_high_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    cadence_target: Mapped[int | None] = mapped_column(Integer, nullable=True)
    repeat_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)

    workout = relationship("Workout", back_populates="steps")
