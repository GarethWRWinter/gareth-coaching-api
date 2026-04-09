"""Pydantic schemas for training plans, phases, workouts, and steps."""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


# --- Workout Steps ---

class WorkoutStepResponse(BaseModel):
    """A single step within a structured workout."""
    id: str
    step_order: int
    step_type: str
    duration_seconds: int
    power_target_pct: float | None = None
    power_low_pct: float | None = None
    power_high_pct: float | None = None
    cadence_target: int | None = None
    repeat_count: int | None = None
    notes: str | None = None

    model_config = ConfigDict(from_attributes=True)


# --- Workouts ---

class WorkoutResponse(BaseModel):
    """Summary of a planned workout."""
    id: str
    scheduled_date: date
    title: str
    description: str | None = None
    workout_type: str
    planned_duration_seconds: int | None = None
    planned_tss: float | None = None
    planned_if: float | None = None
    status: str
    actual_ride_id: str | None = None
    sort_order: int = 0

    model_config = ConfigDict(from_attributes=True)


class WorkoutDetailResponse(WorkoutResponse):
    """Workout with full step details."""
    steps: list[WorkoutStepResponse] = []


class WorkoutUpdateRequest(BaseModel):
    """Update a workout's status or link a ride."""
    status: str | None = None
    actual_ride_id: str | None = None


class WorkoutLinkRideRequest(BaseModel):
    """Link an actual ride to a workout."""
    ride_id: str


# --- Training Phases ---

class TrainingPhaseResponse(BaseModel):
    """A phase within a training plan."""
    id: str
    phase_type: str
    start_date: date
    end_date: date
    target_weekly_tss: float | None = None
    target_weekly_hours: float | None = None
    focus: str | None = None
    sort_order: int = 0
    workout_count: int = 0

    model_config = ConfigDict(from_attributes=True)


# --- Training Plans ---

class PlanGenerateRequest(BaseModel):
    """Request to generate a new training plan."""
    goal_event_id: str | None = None
    periodization_model: str = Field(
        "traditional",
        description="traditional, polarized, or sweet_spot",
    )
    name: str | None = None


class TrainingPlanResponse(BaseModel):
    """Training plan summary."""
    id: str
    name: str
    goal_event_id: str | None = None
    start_date: date
    end_date: date
    status: str
    periodization_model: str
    created_at: datetime | None = None
    total_weeks: int = 0
    phase_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class TrainingPlanDetailResponse(TrainingPlanResponse):
    """Plan with phases."""
    phases: list[TrainingPhaseResponse] = []


class PlanListResponse(BaseModel):
    """List of training plans."""
    plans: list[TrainingPlanResponse]
    total: int


class PlanWorkoutsResponse(BaseModel):
    """Calendar view of plan workouts."""
    plan_id: str
    workouts: list[WorkoutResponse]
    total: int


# --- Exports ---

class ExportResponse(BaseModel):
    """Export metadata."""
    filename: str
    format: str
    content_type: str
    size_bytes: int
