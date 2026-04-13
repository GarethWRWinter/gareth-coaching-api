"""API endpoints for Coach Marco's proactive presence."""

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_user
from app.core.exceptions import NotFoundException
from app.database import get_db
from app.models.ride import Ride
from app.models.user import User
from app.services.coach_insights_service import (
    explain_metric,
    generate_daily_nudge,
    generate_ride_debrief,
)

router = APIRouter(prefix="/coach", tags=["coach-insights"])


# --- Schemas ---

class NudgeResponse(BaseModel):
    nudge: str
    generated_at: str
    cached: bool = False


class DebriefResponse(BaseModel):
    debrief: str
    generated_at: str
    cached: bool = False


class ExplainRequest(BaseModel):
    metric_name: str
    metric_value: str | float


class ExplainResponse(BaseModel):
    explanation: str


# --- Endpoints ---

@router.get("/nudge", response_model=NudgeResponse)
def get_daily_nudge(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get today's coaching nudge from Marco. Cached per day."""
    return generate_daily_nudge(db, current_user)


@router.get("/ride-debrief/{ride_id}", response_model=DebriefResponse)
def get_ride_debrief(
    ride_id: str,
    force: bool = Query(False),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get Marco's post-ride debrief. Cached on the ride record."""
    ride = (
        db.query(Ride)
        .filter(Ride.id == ride_id, Ride.user_id == current_user.id)
        .first()
    )
    if not ride:
        raise NotFoundException(detail="Ride not found")
    return generate_ride_debrief(db, current_user, ride, force=force)


@router.post("/explain", response_model=ExplainResponse)
def explain_metric_endpoint(
    body: ExplainRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Ask Marco to explain a metric in your personal context."""
    return explain_metric(db, current_user, body.metric_name, body.metric_value)
