"""
Automatic Dropbox sync scheduler.

Runs as a background asyncio task within the FastAPI process.
Periodically checks all connected Dropbox accounts for new FIT files
and imports them automatically.

Features:
- Configurable poll interval (default: 15 minutes)
- Per-user sync with independent error handling
- Automatic PMC recalculation after importing new rides
- Graceful shutdown on app stop
- Logging for monitoring
"""

import asyncio
import logging
from datetime import date, datetime, timezone

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.integration import DropboxToken
from app.models.user import User
from app.services.dropbox_service import sync_fit_files
from app.services.metrics_service import recalculate_from_date

logger = logging.getLogger(__name__)

# Default poll interval in seconds (15 minutes)
DEFAULT_POLL_INTERVAL = 15 * 60

# Maximum files to sync per poll per user
SYNC_BATCH_SIZE = 20

# Global reference to the running task so we can cancel on shutdown
_sync_task: asyncio.Task | None = None


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
