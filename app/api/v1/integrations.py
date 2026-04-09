"""Strava integration API endpoints."""

import asyncio
import logging

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_user
from app.config import settings
from app.core.exceptions import BadRequestException
from app.database import get_db
from app.models.user import User
from app.services import strava_service
from app.services.metrics_service import recalculate_from_date

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/integrations", tags=["integrations"])


@router.get("/strava/auth-url")
def get_strava_auth_url(current_user: User = Depends(get_current_user)):
    """Get Strava OAuth authorization URL (includes user ID in state)."""
    url = strava_service.get_auth_url(state=str(current_user.id))
    return {"auth_url": url}


@router.get("/strava/callback")
async def strava_callback(
    code: str = Query(...),
    state: str = Query(""),
    scope: str = Query(""),
    db: Session = Depends(get_db),
):
    """
    Handle Strava OAuth callback (exchange code for tokens).
    This endpoint is unauthenticated — the user ID comes from the state parameter.
    Redirects back to the frontend settings page after connecting.
    """
    frontend_url = settings.frontend_url or "http://localhost:3000"
    frontend_url = f"{frontend_url}/dashboard/settings"

    if not state:
        return RedirectResponse(f"{frontend_url}?strava=error&reason=missing_state")

    user_id = state

    try:
        token = await strava_service.exchange_code(db, user_id, code)

        # Start historical backfill in background (only on first connect)
        if not token.backfill_status or token.backfill_status == "failed":
            asyncio.create_task(
                strava_service.run_backfill_background(user_id)
            )
            logger.info("Started Strava backfill for user %s", user_id)

        return RedirectResponse(f"{frontend_url}?strava=connected")
    except Exception as e:
        logger.error("Strava callback failed: %s", str(e))
        return RedirectResponse(f"{frontend_url}?strava=error&reason={str(e)}")


@router.post("/strava/sync")
async def sync_strava(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Manually trigger Strava activity sync (recent rides only)."""
    try:
        rides = await strava_service.sync_activities(db, current_user)

        # Recalculate PMC for any new rides with TSS
        for ride in rides:
            if ride.tss and ride.ride_date:
                rd = ride.ride_date
                if hasattr(rd, 'date'):
                    rd = rd.date()
                recalculate_from_date(db, current_user.id, rd)

        return {
            "synced": len(rides),
            "rides": [
                {"id": r.id, "title": r.title, "date": str(r.ride_date)}
                for r in rides
            ],
        }
    except ValueError as e:
        raise BadRequestException(detail=str(e))


@router.get("/strava/status")
def strava_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Check Strava connection status including backfill progress."""
    status = strava_service.get_connection_status(db, current_user.id)
    backfill = strava_service.get_backfill_status(db, current_user.id)
    if backfill:
        status["backfill"] = backfill
    return status


@router.post("/strava/backfill")
async def start_backfill(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Manually trigger historical backfill (re-run if failed or import new)."""
    backfill = strava_service.get_backfill_status(db, current_user.id)
    if backfill and backfill["status"] == "running":
        raise BadRequestException(detail="Backfill already in progress")

    asyncio.create_task(
        strava_service.run_backfill_background(current_user.id)
    )
    return {"status": "backfill_started"}


@router.post("/strava/backfill-segments")
async def start_segment_backfill(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Backfill segment data for existing rides with Strava activity IDs."""
    asyncio.create_task(
        strava_service.run_segment_backfill_background(current_user.id)
    )
    return {"status": "segment_backfill_started"}


@router.delete("/strava")
def disconnect_strava(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Disconnect Strava integration."""
    strava_service.disconnect(db, current_user.id)
    return {"status": "disconnected"}


# ---------------------------------------------------------------------------
# Strava Webhook Endpoints (no auth — called by Strava servers)
# ---------------------------------------------------------------------------

@router.get("/strava/webhook")
async def strava_webhook_verify(
    request: Request,
):
    """
    Strava webhook subscription validation.
    Strava sends a GET with hub.mode, hub.challenge, hub.verify_token.
    We must respond with {"hub.challenge": "<value>"} within 2 seconds.
    """
    params = request.query_params
    mode = params.get("hub.mode")
    challenge = params.get("hub.challenge")
    verify_token = params.get("hub.verify_token")

    if mode == "subscribe" and verify_token == settings.strava_webhook_verify_token:
        logger.info("Strava webhook subscription verified")
        return JSONResponse(content={"hub.challenge": challenge})

    logger.warning("Strava webhook verification failed: mode=%s, token=%s", mode, verify_token)
    return JSONResponse(status_code=403, content={"error": "Verification failed"})


@router.post("/strava/webhook")
async def strava_webhook_receive(request: Request):
    """
    Receive Strava webhook events.
    Must respond with 200 within 2 seconds — processing happens in background.
    """
    try:
        event = await request.json()
    except Exception:
        return JSONResponse(status_code=400, content={"error": "Invalid JSON"})

    logger.info(
        "Strava webhook event: %s %s (object_id=%s, owner=%s)",
        event.get("object_type"),
        event.get("aspect_type"),
        event.get("object_id"),
        event.get("owner_id"),
    )

    # Process in background so we respond to Strava within 2s
    asyncio.create_task(strava_service.handle_webhook_event(event))

    return JSONResponse(status_code=200, content={"status": "ok"})
