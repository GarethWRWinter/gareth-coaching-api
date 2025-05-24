import math
from typing import List, Dict
from datetime import datetime

from scripts.ride_database import load_all_rides

def exponential_weighted_moving_average(data: List[float], alpha: float) -> List[float]:
    if not data:
        return []
    ewma = [data[0]]
    for value in data[1:]:
        ewma.append(alpha * value + (1 - alpha) * ewma[-1])
    return ewma

def analyze_trends() -> Dict:
    rides = load_all_rides()
    if not rides:
        return {
            "error": "No ride data available",
            "CTL": 0,
            "ATL": 0,
            "TSB": 0,
            "weekly_load": {},
            "flags": []
        }

    # Sort rides by date
    rides.sort(key=lambda r: r.get("start_time", ""))

    # Extract TSS and dates
    dates = []
    tss_values = []

    for ride in rides:
        tss = ride.get("TSS")
        start_time = ride.get("start_time")
        if tss is not None and start_time:
            try:
                tss_values.append(float(tss))
                dates.append(datetime.fromisoformat(start_time))
            except Exception:
                continue

    if not tss_values:
        return {
            "error": "No valid TSS data found",
            "CTL": 0,
            "ATL": 0,
            "TSB": 0,
            "weekly_load": {},
            "flags": []
        }

    # CTL ~ 42-day EWMA, ATL ~ 7-day EWMA
    ctl = exponential_weighted_moving_average(tss_values, alpha=1 / 42)
    atl = exponential_weighted_moving_average(tss_values, alpha=1 / 7)

    # Compute current values
    ctl_value = round(ctl[-1], 2)
    atl_value = round(atl[-1], 2)
    tsb_value = round(ctl_value - atl_value, 2)

    # Weekly load aggregation
    weekly_load = {}
    for date, tss in zip(dates, tss_values):
        week_key = f"{date.year}-W{date.isocalendar().week}"
        weekly_load.setdefault(week_key, 0)
        weekly_load[week_key] += tss

    return {
        "CTL": ctl_value,
        "ATL": atl_value,
        "TSB": tsb_value,
        "weekly_load": weekly_load,
        "flags": []  # Optional: add fatigue/warning tags later
    }
