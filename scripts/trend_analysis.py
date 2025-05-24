import datetime
from typing import Dict, Any, List
from scripts.ride_database import load_all_rides
from scripts.constants import DEFAULT_FTP


def compute_trend_metrics() -> Dict[str, Any]:
    """
    Analyze all stored rides and compute long-term training metrics.
    Returns:
        A dictionary with CTL, ATL, TSB, FTP, 7-day tags, and weekly load.
    """
    rides = load_all_rides()
    if not rides:
        return {
            "message": "No ride data available for trend analysis."
        }

    rides_sorted = sorted(rides, key=lambda x: x["start_time"])
    today = datetime.datetime.now().date()

    # Extract rolling data
    tss_by_day = {}
    for ride in rides_sorted:
        ride_day = ride["start_time"].date()
        tss_by_day.setdefault(ride_day, 0)
        tss_by_day[ride_day] += ride.get("tss", 0)

    all_days = sorted(tss_by_day.keys())
    ctl, atl = 0, 0
    ctl_constant = 1 - pow(2.718, -1 / 42)  # ~0.023
    atl_constant = 1 - pow(2.718, -1 / 7)   # ~0.133

    ctl_by_day = {}
    atl_by_day = {}

    for day in all_days:
        tss = tss_by_day[day]
        ctl = ctl + ctl_constant * (tss - ctl)
        atl = atl + atl_constant * (tss - atl)
        ctl_by_day[day] = ctl
        atl_by_day[day] = atl

    latest_day = all_days[-1]
    tsb = ctl_by_day[latest_day] - atl_by_day[latest_day]

    # Weekly load and tag aggregation
    one_week_ago = today - datetime.timedelta(days=7)
    recent_rides = [r for r in rides_sorted if r["start_time"].date() >= one_week_ago]

    weekly_load = sum(r.get("tss", 0) for r in recent_rides)
    tags = [tag for r in recent_rides for tag in r.get("tags", [])]
    tag_counts = {tag: tags.count(tag) for tag in set(tags)}

    # Latest known FTP
    latest_ftp = max((r.get("ftp", 0) or 0) for r in rides_sorted if r.get("ftp")) or DEFAULT_FTP

    return {
        "ftp": latest_ftp,
        "ctl": round(ctl_by_day[latest_day], 2),
        "atl": round(atl_by_day[latest_day], 2),
        "tsb": round(tsb, 2),
        "weekly_load": round(weekly_load, 2),
        "recent_tags": tag_counts
    }
