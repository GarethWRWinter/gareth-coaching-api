"""Performance Management Chart (PMC) and daily metrics calculation."""

from datetime import date, datetime, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.formulas import atl_update, ctl_update
from app.models.metrics import DailyMetrics
from app.models.ride import Ride, RideData


def recalculate_from_date(db: Session, user_id: str, start_date: date) -> None:
    """
    Recalculate CTL/ATL/TSB from start_date forward to today.

    This is called after any ride is added, modified, or deleted.
    Computes forward from the last known values before start_date.
    """
    today = date.today()

    # Get the day before start_date to seed CTL/ATL
    prev_day = start_date - timedelta(days=1)
    prev_metrics = (
        db.query(DailyMetrics)
        .filter(DailyMetrics.user_id == user_id, DailyMetrics.date == prev_day)
        .first()
    )
    prev_ctl = prev_metrics.ctl if prev_metrics else 0.0
    prev_atl = prev_metrics.atl if prev_metrics else 0.0

    # Get daily TSS sums from rides
    daily_tss = {}
    rides_query = (
        db.query(Ride)
        .filter(
            Ride.user_id == user_id,
            Ride.tss.isnot(None),
        )
        .all()
    )
    # Group by date in Python (works with both SQLite and PostgreSQL)
    for ride in rides_query:
        if ride.ride_date is None:
            continue
        rd = ride.ride_date
        if isinstance(rd, datetime):
            ride_day = rd.date()
        else:
            ride_day = rd
        if start_date <= ride_day <= today:
            daily_tss[ride_day] = daily_tss.get(ride_day, 0.0) + float(ride.tss)

    # Calculate CTL/ATL/TSB for each day from start_date to today
    current_date = start_date
    current_ctl = prev_ctl
    current_atl = prev_atl

    # For ramp rate, track CTL from 7 days ago
    ctl_7_days_ago = prev_ctl

    while current_date <= today:
        tss = daily_tss.get(current_date, 0.0)

        current_ctl = ctl_update(current_ctl, tss)
        current_atl = atl_update(current_atl, tss)
        current_tsb = current_ctl - current_atl

        # Ramp rate: CTL change per week
        ramp_rate = (current_ctl - ctl_7_days_ago)

        # Upsert daily_metrics row
        existing = (
            db.query(DailyMetrics)
            .filter(DailyMetrics.user_id == user_id, DailyMetrics.date == current_date)
            .first()
        )

        if existing:
            existing.tss = tss
            existing.ctl = round(current_ctl, 2)
            existing.atl = round(current_atl, 2)
            existing.tsb = round(current_tsb, 2)
            existing.ramp_rate = round(ramp_rate, 2)
        else:
            dm = DailyMetrics(
                user_id=user_id,
                date=current_date,
                tss=tss,
                ctl=round(current_ctl, 2),
                atl=round(current_atl, 2),
                tsb=round(current_tsb, 2),
                ramp_rate=round(ramp_rate, 2),
            )
            db.add(dm)

        # Shift the 7-day-ago CTL window
        if current_date >= start_date + timedelta(days=7):
            day_7_ago = current_date - timedelta(days=7)
            m = (
                db.query(DailyMetrics)
                .filter(DailyMetrics.user_id == user_id, DailyMetrics.date == day_7_ago)
                .first()
            )
            if m:
                ctl_7_days_ago = m.ctl

        current_date += timedelta(days=1)

    db.commit()


def get_pmc_data(
    db: Session, user_id: str,
    start_date: date | None = None,
    end_date: date | None = None,
) -> list[DailyMetrics]:
    """Get PMC data for a date range."""
    query = db.query(DailyMetrics).filter(DailyMetrics.user_id == user_id)

    if start_date:
        query = query.filter(DailyMetrics.date >= start_date)
    if end_date:
        query = query.filter(DailyMetrics.date <= end_date)

    return query.order_by(DailyMetrics.date).all()


def get_current_fitness(db: Session, user_id: str) -> dict:
    """Get the most recent CTL/ATL/TSB values."""
    latest = (
        db.query(DailyMetrics)
        .filter(DailyMetrics.user_id == user_id)
        .order_by(DailyMetrics.date.desc())
        .first()
    )
    if not latest:
        return {"ctl": 0.0, "atl": 0.0, "tsb": 0.0, "ramp_rate": 0.0}

    return {
        "ctl": latest.ctl,
        "atl": latest.atl,
        "tsb": latest.tsb,
        "ramp_rate": latest.ramp_rate or 0.0,
    }


def _compute_power_profile(
    db: Session, ride_ids: list, ride_dates: dict, durations: list
) -> dict[int, dict]:
    """Compute best efforts for a set of rides. Shared by all-time and recent profiles."""
    from collections import defaultdict
    from app.core.formulas import best_efforts

    best: dict[int, dict] = {
        d: {"best_power": 0.0, "ride_id": None, "ride_date": None}
        for d in durations
    }

    if not ride_ids:
        return best

    # Batch-load all power data in one query, grouped by ride
    all_rows = (
        db.query(RideData.ride_id, RideData.power)
        .filter(RideData.ride_id.in_(ride_ids))
        .order_by(RideData.ride_id, RideData.elapsed_seconds)
        .yield_per(50000)
        .all()
    )

    ride_power: dict[str, list[float]] = defaultdict(list)
    for row in all_rows:
        ride_power[row.ride_id].append(row.power or 0)

    for ride_id, power_data in ride_power.items():
        if not power_data:
            continue

        efforts = best_efforts(power_data, durations)
        for duration, power in efforts.items():
            if power > best[duration]["best_power"]:
                rd = ride_dates.get(ride_id)
                if rd and hasattr(rd, "date") and callable(rd.date):
                    rd = rd.date()
                best[duration] = {
                    "best_power": power,
                    "ride_id": str(ride_id),
                    "ride_date": rd,
                }

    return best


def get_all_time_power_profile(db: Session, user_id: str) -> dict[int, dict]:
    """
    Get best-ever power for standard durations.
    Optimised: only scans top rides by max_power, NP, and duration.
    """
    from app.core.constants import POWER_PROFILE_DURATIONS

    durations = list(POWER_PROFILE_DURATIONS.values())

    top_by_power = (
        db.query(Ride.id)
        .filter(Ride.user_id == user_id, Ride.max_power.isnot(None))
        .order_by(Ride.max_power.desc())
        .limit(200)
        .all()
    )
    top_by_np = (
        db.query(Ride.id)
        .filter(Ride.user_id == user_id, Ride.normalized_power.isnot(None))
        .order_by(Ride.normalized_power.desc())
        .limit(100)
        .all()
    )
    top_by_duration = (
        db.query(Ride.id)
        .filter(Ride.user_id == user_id, Ride.average_power.isnot(None))
        .order_by(Ride.duration_seconds.desc())
        .limit(50)
        .all()
    )

    ride_ids = list({r.id for r in top_by_power + top_by_np + top_by_duration})
    ride_dates = {
        r.id: r.ride_date
        for r in db.query(Ride.id, Ride.ride_date).filter(Ride.id.in_(ride_ids)).all()
    }

    return _compute_power_profile(db, ride_ids, ride_dates, durations)


def get_recent_power_profile(db: Session, user_id: str, days: int = 90) -> dict[int, dict]:
    """
    Get best power for standard durations within the last N days (default 90).
    90 days is standard for 'current form' in cycling analytics.
    """
    from app.core.constants import POWER_PROFILE_DURATIONS

    durations = list(POWER_PROFILE_DURATIONS.values())
    cutoff = date.today() - timedelta(days=days)

    rides = (
        db.query(Ride.id, Ride.ride_date)
        .filter(
            Ride.user_id == user_id,
            Ride.average_power.isnot(None),
            Ride.ride_date >= cutoff,
        )
        .all()
    )

    ride_ids = [r.id for r in rides]
    ride_dates = {r.id: r.ride_date for r in rides}

    return _compute_power_profile(db, ride_ids, ride_dates, durations)


def get_weekly_training_load(
    db: Session, user_id: str, weeks: int = 12,
) -> list[dict]:
    """
    Get weekly TSS, ride count, duration, and avg IF for the last N weeks.
    Returns list of dicts sorted oldest-to-newest.
    """
    from datetime import timedelta

    today = date.today()
    # Start from the Monday N weeks ago
    start = today - timedelta(weeks=weeks, days=today.weekday())

    rides = (
        db.query(Ride)
        .filter(
            Ride.user_id == user_id,
            Ride.ride_date >= start,
            Ride.tss.isnot(None),
        )
        .all()
    )

    # Bucket into ISO weeks
    weekly: dict[date, dict] = {}
    current = start
    while current <= today:
        weekly[current] = {
            "week_start": current,
            "total_tss": 0.0,
            "ride_count": 0,
            "total_duration_seconds": 0,
            "if_sum": 0.0,
            "if_count": 0,
        }
        current += timedelta(weeks=1)

    for ride in rides:
        rd = ride.ride_date
        if isinstance(rd, datetime):
            rd = rd.date()
        # Find which week this ride belongs to
        week_start = rd - timedelta(days=rd.weekday())
        if week_start not in weekly:
            # Edge case: ride before our window
            continue
        w = weekly[week_start]
        w["total_tss"] += float(ride.tss or 0)
        w["ride_count"] += 1
        w["total_duration_seconds"] += ride.duration_seconds or 0
        if ride.intensity_factor and ride.intensity_factor > 0:
            w["if_sum"] += ride.intensity_factor
            w["if_count"] += 1

    result = []
    for ws in sorted(weekly.keys()):
        w = weekly[ws]
        avg_if = round(w["if_sum"] / w["if_count"], 3) if w["if_count"] > 0 else None
        result.append({
            "week_start": w["week_start"],
            "total_tss": round(w["total_tss"], 1),
            "ride_count": w["ride_count"],
            "total_duration_seconds": w["total_duration_seconds"],
            "avg_intensity_factor": avg_if,
        })

    return result


def get_ride_zone_distribution(
    db: Session, ride_id: str, ftp: int,
) -> dict:
    """
    Calculate time spent in each power zone for a specific ride.
    Uses per-second power data from ride_data table.
    """
    from app.core.formulas import power_zones

    rows = (
        db.query(RideData.power)
        .filter(RideData.ride_id == ride_id, RideData.power.isnot(None))
        .all()
    )

    if not rows or ftp <= 0:
        return {"zones": [], "total_seconds": 0, "ftp": ftp}

    zones = power_zones(ftp)
    zone_names = {
        "Z1": "Active Recovery",
        "Z2": "Endurance",
        "Z3": "Tempo",
        "Z4": "Threshold",
        "Z5": "VO2 Max",
        "Z6": "Anaerobic",
        "Z7": "Neuromuscular",
    }

    # Build sorted list of (zone_key, low, high, name)
    zone_list = []
    for key in sorted(zones.keys()):
        z = zones[key]
        zone_list.append((key, z["low"], z["high"], zone_names.get(key, key)))

    # Count seconds in each zone
    zone_seconds = {key: 0 for key, _, _, _ in zone_list}
    total = 0

    for (power,) in rows:
        if power is None or power < 0:
            continue
        total += 1
        for key, low, high, _ in zone_list:
            if low <= power <= high:
                zone_seconds[key] += 1
                break
        else:
            # Above Z7
            if power > zone_list[-1][2]:
                zone_seconds[zone_list[-1][0]] += 1

    result_zones = []
    for key, low, high, name in zone_list:
        secs = zone_seconds[key]
        pct = round(secs / total * 100, 1) if total > 0 else 0
        result_zones.append({
            "zone": key,
            "zone_name": name,
            "low_watts": low,
            "high_watts": high,
            "seconds": secs,
            "percentage": pct,
        })

    return {
        "zones": result_zones,
        "total_seconds": total,
        "ftp": ftp,
    }


def get_ftp_history(db: Session, user_id: str) -> list[dict]:
    """
    Get FTP history from ride data — extracts distinct FTP values over time.
    """
    rides = (
        db.query(Ride.ride_date, Ride.ftp_at_time)
        .filter(
            Ride.user_id == user_id,
            Ride.ftp_at_time.isnot(None),
            Ride.ftp_at_time > 0,
        )
        .order_by(Ride.ride_date.asc())
        .all()
    )

    if not rides:
        return []

    # Only keep entries where FTP changed
    history = []
    last_ftp = None
    for ride_date, ftp in rides:
        if ftp != last_ftp:
            rd = ride_date
            if isinstance(rd, datetime):
                rd = rd.date()
            history.append({
                "date": rd,
                "ftp": ftp,
                "source": "device",
            })
            last_ftp = ftp

    return history
