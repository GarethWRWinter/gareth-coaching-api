"""Training plan and workout API endpoints."""

from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_user
from app.core.exceptions import BadRequestException, NotFoundException
from app.database import get_db
from app.models.user import User
from app.schemas.training import (
    PlanGenerateRequest,
    PlanListResponse,
    PlanWorkoutsResponse,
    TrainingPlanDetailResponse,
    TrainingPlanResponse,
    TrainingPhaseResponse,
    WorkoutAssessmentResponse,
    WorkoutDetailResponse,
    WorkoutLinkRideRequest,
    WorkoutResponse,
    WorkoutStepResponse,
    WorkoutUpdateRequest,
)
from app.services.plan_service import (
    generate_plan,
    get_plan,
    get_plan_workouts,
    get_plans,
    get_workout,
    get_workouts_by_date,
    link_ride_to_workout,
    update_workout_status,
)
from app.services.workout_assessment_service import generate_assessment

router = APIRouter(tags=["training"])


# --- Plans ---

@router.get("/plans", response_model=PlanListResponse)
def list_plans(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all training plans."""
    plans = get_plans(db, current_user.id)
    return PlanListResponse(
        plans=[_plan_to_response(p) for p in plans],
        total=len(plans),
    )


@router.post("/plans/generate", response_model=TrainingPlanDetailResponse, status_code=201)
def generate_training_plan(
    body: PlanGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Generate a new periodized training plan based on goals and fitness."""
    try:
        plan = generate_plan(
            db, current_user,
            goal_event_id=body.goal_event_id,
            periodization_model=body.periodization_model,
            name=body.name,
        )
    except ValueError as e:
        raise BadRequestException(detail=str(e))

    return _plan_to_detail_response(plan)


@router.get("/plans/{plan_id}", response_model=TrainingPlanDetailResponse)
def get_training_plan(
    plan_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a training plan with phases."""
    plan = get_plan(db, plan_id, current_user.id)
    if not plan:
        raise NotFoundException(detail="Plan not found")
    return _plan_to_detail_response(plan)


@router.get("/plans/{plan_id}/workouts", response_model=PlanWorkoutsResponse)
def list_plan_workouts(
    plan_id: str,
    start_date: date | None = None,
    end_date: date | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all workouts for a plan (calendar data)."""
    workouts = get_plan_workouts(db, plan_id, current_user.id, start_date, end_date)
    return PlanWorkoutsResponse(
        plan_id=plan_id,
        workouts=[WorkoutResponse.model_validate(w) for w in workouts],
        total=len(workouts),
    )


# --- Workouts ---

@router.get("/workouts", response_model=list[WorkoutResponse])
def list_workouts(
    target_date: date | None = Query(None, alias="date"),
    week: date | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List workouts by date or week."""
    workouts = get_workouts_by_date(db, current_user.id, target_date, week)
    return [WorkoutResponse.model_validate(w) for w in workouts]


@router.get("/workouts/{workout_id}", response_model=WorkoutDetailResponse)
def get_workout_detail(
    workout_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a workout with full step details."""
    workout = get_workout(db, workout_id, current_user.id)
    if not workout:
        raise NotFoundException(detail="Workout not found")

    return WorkoutDetailResponse(
        **{k: v for k, v in WorkoutResponse.model_validate(workout).model_dump().items()},
        steps=[WorkoutStepResponse.model_validate(s) for s in workout.steps],
    )


@router.patch("/workouts/{workout_id}", response_model=WorkoutResponse)
def update_workout(
    workout_id: str,
    body: WorkoutUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update workout status (completed/skipped/modified)."""
    workout = get_workout(db, workout_id, current_user.id)
    if not workout:
        raise NotFoundException(detail="Workout not found")

    if body.status:
        try:
            workout = update_workout_status(db, workout, body.status, body.actual_ride_id)
        except ValueError as e:
            raise BadRequestException(detail=str(e))

    return WorkoutResponse.model_validate(workout)


@router.post("/workouts/{workout_id}/link-ride", response_model=WorkoutResponse)
def link_ride(
    workout_id: str,
    body: WorkoutLinkRideRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Link an actual ride to a planned workout."""
    workout = get_workout(db, workout_id, current_user.id)
    if not workout:
        raise NotFoundException(detail="Workout not found")

    workout = link_ride_to_workout(db, workout, body.ride_id)
    return WorkoutResponse.model_validate(workout)


@router.get(
    "/workouts/{workout_id}/assessment",
    response_model=WorkoutAssessmentResponse,
)
def get_workout_assessment(
    workout_id: str,
    force: bool = Query(False, description="Regenerate feedback even if cached"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Score the actual ride against the planned workout and return supportive
    feedback from Coach Marco plus suggested adjustments to upcoming days.

    The numeric score is always recomputed; the written feedback is cached on
    the workout row and only regenerated when `force=true` or when no cached
    feedback exists yet.
    """
    workout = get_workout(db, workout_id, current_user.id)
    if not workout:
        raise NotFoundException(detail="Workout not found")
    if not workout.actual_ride_id:
        raise BadRequestException(detail="No ride is linked to this workout yet")

    try:
        workout = generate_assessment(db, current_user, workout, force=force)
    except ValueError as e:
        raise BadRequestException(detail=str(e))

    return WorkoutAssessmentResponse(
        workout_id=workout.id,
        score=workout.execution_score or 0.0,
        feedback=workout.execution_feedback or "",
        adjustments=workout.execution_adjustments or [],
        assessed_at=workout.execution_assessed_at,
    )


# --- Helpers ---

def _plan_to_response(plan) -> TrainingPlanResponse:
    """Convert TrainingPlan to response schema."""
    start = plan.start_date
    end = plan.end_date
    total_weeks = 0
    if start and end:
        total_weeks = max(1, (end - start).days // 7)

    return TrainingPlanResponse(
        id=plan.id,
        name=plan.name,
        goal_event_id=plan.goal_event_id,
        start_date=plan.start_date,
        end_date=plan.end_date,
        status=plan.status,
        periodization_model=plan.periodization_model,
        created_at=plan.created_at,
        total_weeks=total_weeks,
        phase_count=len(plan.phases) if plan.phases else 0,
    )


def _plan_to_detail_response(plan) -> TrainingPlanDetailResponse:
    """Convert TrainingPlan to detail response with phases."""
    base = _plan_to_response(plan)

    phases = []
    for p in plan.phases:
        phases.append(TrainingPhaseResponse(
            id=p.id,
            phase_type=p.phase_type,
            start_date=p.start_date,
            end_date=p.end_date,
            target_weekly_tss=p.target_weekly_tss,
            target_weekly_hours=p.target_weekly_hours,
            focus=p.focus,
            sort_order=p.sort_order,
            workout_count=len(p.workouts) if p.workouts else 0,
        ))

    return TrainingPlanDetailResponse(
        **base.model_dump(),
        phases=phases,
    )
