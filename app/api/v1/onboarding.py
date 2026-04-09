"""Onboarding quiz API endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_user
from app.core.exceptions import BadRequestException
from app.database import get_db
from app.models.user import User
from app.schemas.onboarding import (
    OnboardingQuizRequest,
    OnboardingResponse,
    OnboardingStatusResponse,
)
from app.services.onboarding_service import get_onboarding_response, get_onboarding_status, submit_quiz

router = APIRouter(prefix="/onboarding", tags=["onboarding"])


@router.post("/quiz", response_model=OnboardingResponse, status_code=201)
def submit_onboarding_quiz(
    body: OnboardingQuizRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Submit onboarding quiz answers. Replaces previous answers if re-submitted."""
    try:
        response = submit_quiz(
            db,
            current_user.id,
            primary_goal=body.primary_goal,
            secondary_goals=body.secondary_goals,
            current_weekly_volume_hours=body.current_weekly_volume_hours,
            years_cycling=body.years_cycling,
            indoor_outdoor_preference=body.indoor_outdoor_preference,
        )
    except ValueError as e:
        raise BadRequestException(detail=str(e))

    return response


@router.get("/status", response_model=OnboardingStatusResponse)
def check_onboarding_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Check if onboarding is complete."""
    status = get_onboarding_status(db, current_user.id)
    return OnboardingStatusResponse(**status)


@router.get("/response", response_model=OnboardingResponse)
def get_quiz_response(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get the full onboarding response (quiz answers)."""
    response = get_onboarding_response(db, current_user.id)
    if not response:
        raise BadRequestException(detail="Onboarding not completed yet")
    return response
