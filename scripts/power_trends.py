# scripts/power_trends.py

from scripts.ride_database import get_all_rides_with_data

def get_power_trends():
    rides = get_all_rides_with_data()
    power_trend = {
        "latest_7_day_avg_power": None,
        "longest_duration": None,
        "highest_tss": None,
    }

    if not rides:
        return power_trend

    total_power = 0
    total_rides = 0
    highest_tss = 0
    longest_duration = 0

    for ride in rides[-7:]:
        total_rides += 1
        total_power += ride.get("avg_power", 0)
        highest_tss = max(highest_tss, ride.get("tss", 0))
        longest_duration = max(longest_duration, ride.get("duration_sec", 0))

    power_trend["latest_7_day_avg_power"] = round(total_power / total_rides, 1) if total_rides > 0 else None
    power_trend["highest_tss"] = highest_tss
    power_trend["longest_duration"] = longest_duration

    return power_trend
