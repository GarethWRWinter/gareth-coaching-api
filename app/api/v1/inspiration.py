"""Daily inspiration endpoint — one line from the sport, every day."""

from fastapi import APIRouter, Depends

from app.api.v1.deps import get_current_user
from app.content.daily_inspiration import todays_inspiration
from app.models.user import User

router = APIRouter(prefix="/inspiration", tags=["inspiration"])


@router.get("/today")
def get_todays_inspiration(current_user: User = Depends(get_current_user)):
    """Today's quote or wisdom. Global and deterministic — one line a day,
    the same for every rider, like a shared stage."""
    return todays_inspiration()
