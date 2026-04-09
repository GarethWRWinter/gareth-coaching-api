"""Post-goal assessment service — results, ride linking, planned-vs-actual analysis."""

from datetime import date, datetime, timedelta

from sqlalchemy.orm import Session

from app.models.onboarding import GoalEvent, GoalStatus
from app.models.ride import Ride


def submit_assessment(db: Session, goal: GoalEvent, data: dict) -> GoalEvent:
    """Store assessment data on a goal event."""
    status_value = data["status"]
    GoalStatus(status_value)  # validate

    goal.status = status_value
    if data.get("actual_ride_id"):
        goal.actual_ride_id = data["actual_ride_id"]
    if data.get("finish_time_seconds") is not None:
        goal.finish_time_seconds = data["finish_time_seconds"]
    if data.get("finish_position") is not None:
        goal.finish_position = data["finish_position"]
    if data.get("finish_position_total") is not None:
        goal.finish_position_total = data["finish_position_total"]
    if data.get("overall_satisfaction") is not None:
        goal.overall_satisfaction = data["overall_satisfaction"]
    if data.get("perceived_exertion") is not None:
        goal.perceived_exertion = data["perceived_exertion"]
    if data.get("assessment_data") is not None:
        goal.assessment_data = data["assessment_data"]

    goal.assessment_completed_at = datetime.utcnow()

    db.commit()
    db.refresh(goal)
    return goal


def get_candidate_rides(db: Session, user_id: str, event_date: date) -> list[Ride]:
    """Find rides within ±1 day of the event date for linking."""
    start = event_date - timedelta(days=1)
    end = event_date + timedelta(days=1)

    return (
        db.query(Ride)
        .filter(
            Ride.user_id == user_id,
            Ride.ride_date >= start,
            Ride.ride_date <= end,
        )
        .order_by(Ride.ride_date)
        .all()
    )


def get_planned_vs_actual(db: Session, goal: GoalEvent) -> dict | None:
    """Compare planned targets with actual ride data."""
    if not goal.actual_ride_id:
        return None

    ride = db.query(Ride).filter(Ride.id == goal.actual_ride_id).first()
    if not ride:
        return None

    target_time = (goal.target_duration_minutes * 60) if goal.target_duration_minutes else None
    actual_time = ride.duration_seconds

    time_delta = None
    time_delta_pct = None
    if target_time and actual_time:
        time_delta = actual_time - target_time
        time_delta_pct = round(time_delta / target_time * 100, 1)

    # Pacing analysis based on variability index
    pacing = "unknown"
    if ride.variability_index:
        vi = ride.variability_index
        if vi <= 1.02:
            pacing = "very_even"
        elif vi <= 1.05:
            pacing = "even"
        elif vi <= 1.10:
            pacing = "moderate_variation"
        else:
            pacing = "erratic"

    return {
        "target_time_seconds": target_time,
        "actual_time_seconds": actual_time,
        "target_np": None,
        "actual_np": round(ride.normalized_power) if ride.normalized_power else None,
        "actual_if": round(ride.intensity_factor, 2) if ride.intensity_factor else None,
        "actual_vi": round(ride.variability_index, 2) if ride.variability_index else None,
        "actual_tss": round(ride.tss, 1) if ride.tss else None,
        "pacing_analysis": pacing,
        "time_delta_seconds": time_delta,
        "time_delta_pct": time_delta_pct,
    }


def get_goals_needing_assessment(db: Session, user_id: str) -> list[GoalEvent]:
    """Return goals where event_date has passed but status is still 'upcoming'."""
    today = date.today()
    return (
        db.query(GoalEvent)
        .filter(
            GoalEvent.user_id == user_id,
            GoalEvent.event_date < today,
            GoalEvent.status == GoalStatus.upcoming,
        )
        .order_by(GoalEvent.event_date.desc())
        .all()
    )
