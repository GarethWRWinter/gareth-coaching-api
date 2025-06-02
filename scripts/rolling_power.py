# scripts/rolling_power.py

from scripts.ride_database import get_all_rides
import pandas as pd
from datetime import datetime, timedelta

def calculate_rolling_power_trends():
    rides = get_all_rides()
    if not rides:
        return {"message": "No ride data available yet."}

    # Build a DataFrame of all second-by-second power data
    power_data = []
    for ride in rides:
        if ride.power_zone_times and "seconds" in ride.power_zone_times:
            start_time = ride.start_time
            seconds_data = ride.power_zone_times["seconds"]
            if seconds_data:
                for sec, zone_power in seconds_data.items():
                    power_data.append({
                        "timestamp": start_time,
                        "power": zone_power
                    })

    if not power_data:
        return {"message": "No detailed power data available."}

    df = pd.DataFrame(power_data)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp")
    df.set_index("timestamp", inplace=True)

    # Rolling best efforts
    durations = {
        "30s": 30,
        "1min": 60,
        "5min": 300,
        "20min": 1200,
        "60min": 3600
    }

    end_date = df.index.max()
    power_trends = {}

    for window in [30, 60, 90]:
        window_days = timedelta(days=window)
        window_start = end_date - window_days
        window_df = df.loc[df.index >= window_start]

        best_efforts = {}
        for label, duration in durations.items():
            rolling_avg = window_df["power"].rolling(window=duration, min_periods=1).mean()
            best_power = rolling_avg.max()
            best_efforts[label] = round(best_power, 2) if pd.notna(best_power) else 0.0

        power_trends[f"{window}-day"] = best_efforts

    return power_trends
