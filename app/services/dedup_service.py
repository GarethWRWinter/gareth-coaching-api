"""
Cross-source ride deduplication.

When a user connects both Strava and Dropbox, the same ride can appear
twice -- once from each source.  Dropbox FIT files carry richer data
(device-calculated NP/TSS/IF, L/R balance, temperature, torque, etc.)
so they are always preferred.

Two rides are considered duplicates when:
  * they belong to the same user
  * they fall on the same calendar date (UTC)
  * their durations are within +/- 5 minutes of each other

The module exposes helpers used by the Strava and Dropbox sync paths
as well as a one-time cleanup routine for existing data.
"""

import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from app.models.ride import Ride, RideData, RideSource
from app.models.segment import SegmentEffort

logger = logging.getLogger(__name__)

# Two rides match if their durations are within this tolerance
DURATION_TOLERANCE_SECONDS = 5 * 60  # 5 minutes


def find_dropbox_duplicate(
    db: Session,
    user_id: str,
    ride_date: datetime,
    duration_seconds: int | None,
) -> Ride | None:
    """Return an existing Dropbox ride that matches the given date/duration."""
    if ride_date is None:
        return None

    # Normalise to UTC date boundaries
    if ride_date.tzinfo is None:
        ride_date = ride_date.replace(tzinfo=timezone.utc)

    day_start = ride_date.replace(hour=0, minute=0, second=0, microsecond=0)
    day_end = day_start + timedelta(days=1)

    query = db.query(Ride).filter(
        Ride.user_id == user_id,
        Ride.source == RideSource.dropbox,
        Ride.ride_date >= day_start,
        Ride.ride_date < day_end,
    )

    candidates = query.all()
    if not candidates:
        return None

    # If we have duration info, narrow by tolerance
    if duration_seconds is not None:
        for c in candidates:
            if c.duration_seconds is None:
                # No duration on the Dropbox ride -- still treat as match
                # if it is the only ride that day.
                continue
            if abs(c.duration_seconds - duration_seconds) <= DURATION_TOLERANCE_SECONDS:
                return c
        # No duration-matched candidate; fall back to single-candidate match
        if len(candidates) == 1:
            return candidates[0]
        return None

    # No duration to compare -- match if there is exactly one Dropbox ride that day
    if len(candidates) == 1:
        return candidates[0]
    return None


def find_strava_duplicate(
    db: Session,
    user_id: str,
    ride_date: datetime,
    duration_seconds: int | None,
) -> Ride | None:
    """Return an existing Strava ride that matches the given date/duration."""
    if ride_date is None:
        return None

    if ride_date.tzinfo is None:
        ride_date = ride_date.replace(tzinfo=timezone.utc)

    day_start = ride_date.replace(hour=0, minute=0, second=0, microsecond=0)
    day_end = day_start + timedelta(days=1)

    query = db.query(Ride).filter(
        Ride.user_id == user_id,
        Ride.source == RideSource.strava,
        Ride.ride_date >= day_start,
        Ride.ride_date < day_end,
    )

    candidates = query.all()
    if not candidates:
        return None

    if duration_seconds is not None:
        for c in candidates:
            if c.duration_seconds is None:
                continue
            if abs(c.duration_seconds - duration_seconds) <= DURATION_TOLERANCE_SECONDS:
                return c
        if len(candidates) == 1:
            return candidates[0]
        return None

    if len(candidates) == 1:
        return candidates[0]
    return None


def merge_strava_into_dropbox(
    db: Session,
    dropbox_ride: Ride,
    strava_ride: Ride,
) -> None:
    """
    Keep the Dropbox ride, copy useful Strava metadata onto it,
    then delete the Strava ride (and its data points).
    """
    # Copy Strava metadata that the Dropbox ride lacks
    if not dropbox_ride.title or dropbox_ride.title == "Dropbox Ride":
        dropbox_ride.title = strava_ride.title

    if not dropbox_ride.strava_activity_id and strava_ride.external_id:
        dropbox_ride.strava_activity_id = strava_ride.external_id

    # Copy Strava achievement/social counts
    if strava_ride.achievement_count is not None:
        dropbox_ride.achievement_count = strava_ride.achievement_count
    if strava_ride.pr_count is not None:
        dropbox_ride.pr_count = strava_ride.pr_count
    if strava_ride.kudos_count is not None:
        dropbox_ride.kudos_count = strava_ride.kudos_count

    # Transfer segment efforts to the Dropbox ride
    db.query(SegmentEffort).filter(
        SegmentEffort.ride_id == strava_ride.id
    ).update({"ride_id": dropbox_ride.id})

    # Delete Strava ride's data points and the ride itself
    db.query(RideData).filter(RideData.ride_id == strava_ride.id).delete()
    db.delete(strava_ride)

    logger.info(
        "Merged Strava ride %s into Dropbox ride %s (strava_activity_id=%s)",
        strava_ride.id,
        dropbox_ride.id,
        dropbox_ride.strava_activity_id,
    )


def cleanup_existing_duplicates(db: Session) -> int:
    """
    One-time cleanup: for every user, find Strava rides that have a
    matching Dropbox ride on the same date with similar duration,
    and remove the Strava version.

    Returns the number of Strava rides removed.
    """
    # Get all users who have rides from both sources
    users_with_both = (
        db.query(Ride.user_id)
        .filter(Ride.source == RideSource.strava)
        .intersect(
            db.query(Ride.user_id).filter(Ride.source == RideSource.dropbox)
        )
        .all()
    )

    total_removed = 0

    for (user_id,) in users_with_both:
        strava_rides = (
            db.query(Ride)
            .filter(Ride.user_id == user_id, Ride.source == RideSource.strava)
            .order_by(Ride.ride_date)
            .all()
        )

        for strava_ride in strava_rides:
            dropbox_match = find_dropbox_duplicate(
                db,
                user_id,
                strava_ride.ride_date,
                strava_ride.duration_seconds,
            )
            if dropbox_match:
                merge_strava_into_dropbox(db, dropbox_match, strava_ride)
                total_removed += 1

        db.commit()

    logger.info("Duplicate cleanup complete: removed %d Strava duplicates", total_removed)
    return total_removed
