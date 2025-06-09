from scripts.ride_database import get_ride_history


def get_all_rides():
    """
    This function wraps get_ride_history to align with the expected usage in trend_analysis.
    """
    return get_ride_history()


def calculate_trend_metrics():
    rides = get_all_rides()
    trend_metrics = []

    for ride in rides:
        trend_metrics.append({
            "ride_id": ride["ride_id"],
            "avg_power": ride["avg_power"],
            "tss": ride["tss"],
            "date": ride["start_time"],
            "duration_sec": ride["duration_sec"],
        })

    return trend_metrics
