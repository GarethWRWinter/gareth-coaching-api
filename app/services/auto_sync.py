"""
Background sync schedulers for Dropbox and Strava.

Two independent asyncio background tasks running inside the FastAPI
process. Each polls all connected users at its configured interval.

- Dropbox: 15-minute default. Picks up new FIT files from each user's
  linked Dropbox folder.
- Strava: 5-minute default. Pulls recent activities for each connected
  user. Serves as a backstop against (a) the webhook subscription being
  disabled, (b) frontend auto-sync only firing when the user opens the
  app. With this loop running, rides flow in within 5 minutes regardless
  of webhook or frontend state.

Features:
- Per-user sync with independent error handling — one bad token does
  not stall the rest.
- Automatic PMC recalculation after importing new rides.
- Graceful shutdown on app stop.
- Logging for monitoring.
"""

import asyncio
import logging
from datetime import date, datetime, timezone

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.integration import DropboxToken, StravaToken
from app.models.user import User
from app.services import strava_service
from app.services.dropbox_service import sync_fit_files
from app.services.metrics_service import recalculate_from_date

logger = logging.getLogger(__name__)

# Default poll interval in seconds (15 minutes)
DEFAULT_POLL_INTERVAL = 15 * 60

# Default Strava poll interval in seconds (5 minutes).
# Matches the frontend `useStravaAutoSync` throttle so push (webhook),
# frontend pull, and backend pull all converge around the same cadence.
DEFAULT_STRAVA_POLL_INTERVAL = 5 * 60

# Maximum files to sync per poll per user
SYNC_BATCH_SIZE = 20

# Global references to the running tasks so we can cancel on shutdown
_sync_task: asyncio.Task | None = None
_strava_sync_task: asyncio.Task | None = None


async def _sync_user(db: Session, user_id: str, email: str) -> int:
    """Sync a single user's Dropbox. Returns number of new rides imported."""
    try:
        rides = await sync_fit_files(db, user_id, limit=SYNC_BATCH_SIZE)
        if rides:
            logger.info(
                "Auto-sync: imported %d new rides for %s", len(rides), email
            )
            # Recalculate PMC from the earliest new ride date
            earliest_date_str = min(r["date"] for r in rides)
            try:
                earliest_date = datetime.fromisoformat(
                    earliest_date_str.replace(" ", "T")
                ).date()
            except (ValueError, AttributeError):
                earliest_date = date.today()

            recalculate_from_date(db, user_id, earliest_date)
            logger.info("Auto-sync: PMC recalculated for %s", email)

        return len(rides)

    except Exception:
        logger.exception("Auto-sync failed for user %s", email)
        return 0


async def _poll_once() -> dict:
    """
    Run one sync pass for all connected Dropbox users.
    Returns {"users_checked": N, "total_rides": N}
    """
    db = SessionLocal()
    try:
        # Find all users with a connected Dropbox token
        tokens = db.query(DropboxToken).all()

        if not tokens:
            return {"users_checked": 0, "total_rides": 0}

        total_rides = 0
        for token in tokens:
            user = db.query(User).filter(User.id == token.user_id).first()
            if not user:
                continue

            count = await _sync_user(db, user.id, user.email)
            total_rides += count

        return {"users_checked": len(tokens), "total_rides": total_rides}

    except Exception:
        logger.exception("Auto-sync poll error")
        return {"users_checked": 0, "total_rides": 0, "error": True}
    finally:
        db.close()


async def _sync_loop(interval: int = DEFAULT_POLL_INTERVAL):
    """
    Main background loop. Polls forever at the given interval.
    Catches all exceptions to keep running.
    """
    logger.info("Auto-sync started (interval: %ds)", interval)

    # Initial delay — let the app fully start up before first sync
    await asyncio.sleep(10)

    while True:
        try:
            logger.debug("Auto-sync: starting poll...")
            result = await _poll_once()

            if result.get("total_rides", 0) > 0:
                logger.info(
                    "Auto-sync poll complete: %d users checked, %d new rides",
                    result["users_checked"],
                    result["total_rides"],
                )
            else:
                logger.debug(
                    "Auto-sync poll complete: %d users, no new files",
                    result["users_checked"],
                )

        except asyncio.CancelledError:
            logger.info("Auto-sync shutting down")
            return
        except Exception:
            logger.exception("Auto-sync unexpected error")

        try:
            await asyncio.sleep(interval)
        except asyncio.CancelledError:
            logger.info("Auto-sync shutting down")
            return


def start_auto_sync(interval: int = DEFAULT_POLL_INTERVAL):
    """
    Start the auto-sync background task.
    Called from FastAPI startup event.
    """
    global _sync_task
    if _sync_task is not None and not _sync_task.done():
        logger.warning("Auto-sync already running")
        return

    _sync_task = asyncio.create_task(_sync_loop(interval))
    logger.info("Auto-sync task created")


def stop_auto_sync():
    """
    Stop the auto-sync background task.
    Called from FastAPI shutdown event.
    """
    global _sync_task
    if _sync_task is not None and not _sync_task.done():
        _sync_task.cancel()
        logger.info("Auto-sync task cancelled")
    _sync_task = None


# ---------------------------------------------------------------------------
# Strava periodic sync — independent background task, parallel to Dropbox
# ---------------------------------------------------------------------------

async def _sync_strava_user(db: Session, user: User) -> int:
    """
    Pull recent Strava activities for one user. Returns count of new rides.
    Errors are caught and logged so one bad token can't stall the whole loop.
    """
    try:
        rides = await strava_service.sync_activities(db, user)
        if rides:
            logger.info(
                "Strava auto-sync: imported %d new rides for %s",
                len(rides),
                user.email,
            )
            # Recalculate PMC from earliest new ride that has TSS.
            scored = [r for r in rides if r.tss and r.ride_date]
            if scored:
                earliest = min(scored, key=lambda r: r.ride_date)
                rd = earliest.ride_date
                if hasattr(rd, "date"):
                    rd = rd.date()
                try:
                    recalculate_from_date(db, user.id, rd)
                except Exception:
                    logger.exception(
                        "Strava auto-sync: PMC recalc failed for %s", user.email
                    )
        return len(rides)
    except Exception:
        logger.exception("Strava auto-sync failed for user %s", user.email)
        return 0


async def _strava_poll_once() -> dict:
    """
    Run one Strava sync pass for all connected users.
    Returns {"users_checked": N, "total_rides": N}
    """
    db = SessionLocal()
    try:
        tokens = db.query(StravaToken).all()
        if not tokens:
            return {"users_checked": 0, "total_rides": 0}

        total_rides = 0
        for token in tokens:
            user = db.query(User).filter(User.id == token.user_id).first()
            if not user:
                continue
            total_rides += await _sync_strava_user(db, user)

        return {"users_checked": len(tokens), "total_rides": total_rides}

    except Exception:
        logger.exception("Strava auto-sync poll error")
        return {"users_checked": 0, "total_rides": 0, "error": True}
    finally:
        db.close()


async def _strava_sync_loop(interval: int = DEFAULT_STRAVA_POLL_INTERVAL):
    """
    Main Strava background loop. Polls every `interval` seconds.
    Catches all exceptions so a transient failure doesn't stop the loop.
    """
    logger.info("Strava auto-sync started (interval: %ds)", interval)

    # Slight stagger from the Dropbox loop so the two don't both hammer the
    # DB at the same instant on startup.
    await asyncio.sleep(20)

    while True:
        try:
            logger.debug("Strava auto-sync: starting poll...")
            result = await _strava_poll_once()

            if result.get("total_rides", 0) > 0:
                logger.info(
                    "Strava auto-sync poll complete: %d users, %d new rides",
                    result["users_checked"],
                    result["total_rides"],
                )
            else:
                logger.debug(
                    "Strava auto-sync poll complete: %d users, no new rides",
                    result["users_checked"],
                )

        except asyncio.CancelledError:
            logger.info("Strava auto-sync shutting down")
            return
        except Exception:
            logger.exception("Strava auto-sync unexpected error")

        try:
            await asyncio.sleep(interval)
        except asyncio.CancelledError:
            logger.info("Strava auto-sync shutting down")
            return


def start_strava_auto_sync(interval: int = DEFAULT_STRAVA_POLL_INTERVAL):
    """
    Start the Strava auto-sync background task.
    Called from FastAPI startup event.
    """
    global _strava_sync_task
    if _strava_sync_task is not None and not _strava_sync_task.done():
        logger.warning("Strava auto-sync already running")
        return

    _strava_sync_task = asyncio.create_task(_strava_sync_loop(interval))
    logger.info("Strava auto-sync task created")


def stop_strava_auto_sync():
    """
    Stop the Strava auto-sync background task.
    Called from FastAPI shutdown event.
    """
    global _strava_sync_task
    if _strava_sync_task is not None and not _strava_sync_task.done():
        _strava_sync_task.cancel()
        logger.info("Strava auto-sync task cancelled")
    _strava_sync_task = None
