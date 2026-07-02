"""Memory API — the Brain.

GET  /memory/graph       → nodes + edges for the Brain page
GET  /memory/reading     → Marco's narrated reading of the graph
PATCH /memory/{id}/hide  → hide-not-delete
PATCH /memory/{id}/unhide
"""

import logging

import anthropic
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_user, get_db
from app.config import settings
from app.models.user import User
from app.services import memory_service

router = APIRouter(prefix="/memory", tags=["memory"])
logger = logging.getLogger(__name__)

HAIKU_MODEL = "claude-haiku-4-5-20251001"


@router.get("/graph")
def get_memory_graph(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return memory_service.get_graph(db, current_user)


@router.get("/reading")
def get_memory_reading(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Marco's short narrated reading of the rider's brain."""
    context = memory_service.get_context(db, current_user, limit=40)
    if not context:
        return {"reading": None}
    coach_name = "Marco"
    try:
        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        resp = client.messages.create(
            model=HAIKU_MODEL,
            max_tokens=220,
            system=(
                f"You are {coach_name}, a warm, direct cycling & life coach. "
                "You are looking at the rider's memory graph — everything you know about them. "
                "Write a 2–3 sentence 'reading of your brain': name the strongest cluster or "
                "thread, point out one meaningful cross-life connection or one quiet corner "
                "worth attention. Speak to the rider as 'you'. No preamble, no sign-off."
            ),
            messages=[{"role": "user", "content": context}],
        )
        return {"reading": resp.content[0].text.strip()}
    except Exception:
        logger.exception("Memory reading failed (user=%s)", current_user.id)
        return {"reading": None}


@router.patch("/{entity_id}/hide")
def hide_entity(
    entity_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    e = memory_service.set_hidden(db, current_user, entity_id, True)
    if not e:
        raise HTTPException(status_code=404, detail="Memory not found")
    return {"id": e.id, "hidden": True}


@router.patch("/{entity_id}/unhide")
def unhide_entity(
    entity_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    e = memory_service.set_hidden(db, current_user, entity_id, False)
    if not e:
        raise HTTPException(status_code=404, detail="Memory not found")
    return {"id": e.id, "hidden": False}
