# scripts/trend_analysis.py

from datetime import datetime, timedelta
from scripts.ride_database import get_all_rides_with_data

def get_trend_analysis():
    rides = get_all_rides_with_data()

    if not rides:
        return {
            "7_day_tss_total": 0,
            "weekly_avg_power": None,
            "weekly_training_days": 0,
            "low_endurance_warning": True,
            "most_common_tag": None,
        }

    now = datetime.utcnow()
    seven_days_ago = now - timedelta(days=7)

    tss_total = 0
    power_total = 0
    ride_days = set()
    endurance_seconds = 0
    tag_counts = {}

    for ride in rides:
        start = ride.get("start_time")
        if isinstance(start, str):
            start = datetime.fromisoformat(start)

        if start and start >= seven_days_ago:
            tss_total += ride.get("tss", 0)
            power_total += ride.get("avg_power", 0)
            ride_days.add(start.date())

            # Count endurance time
            if ride.get("tag") == "Endurance":
                endurance_seconds += ride.get("duration_sec", 0)

            # Track most common tag
            tag = ride.get("tag", "Unclassified")
            tag_counts[tag] = tag_counts.get(tag, 0) + 1

    avg_power = round(power_total / len(ride_days), 1) if ride_days else None
    most_common_tag = max(tag_counts.items(), key=lambda x: x[1])[0] if tag_counts else None
    low_endurance_flag = endurance_seconds < 3600  # less than 1 hour

    return {
        "7_day_tss_total": tss_total,
        "weekly_avg_power": avg_power,
        "weekly_training_days": len(ride_days),
        "low_endurance_warning": low_endurance_flag,
        "most_common_tag": most_common_tag,
    }
