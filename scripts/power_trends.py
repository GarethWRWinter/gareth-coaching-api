import pandas as pd
from scripts.ride_database import get_all_rides_with_data

def get_best_efforts(df, durations):
    best_efforts = {}
    for duration in durations:
        window = int(duration)
        if len(df) >= window:
            rolling = df['power'].rolling(window=window).mean()
            best_efforts[f"{duration}_sec"] = round(rolling.max(), 2)
        else:
            best_efforts[f"{duration}_sec"] = None
    return best_efforts

def get_power_trends():
    rides = get_all_rides_with_data()
    trends = {"30-day": {}, "60-day": {}, "90-day": {}}
    durations = [30, 60, 300, 1200, 3600]  # 30s, 1min, 5min, 20min, 60min

    today = pd.Timestamp.now(tz="UTC")

    for window, label in [(30, "30-day"), (60, "60-day"), (90, "90-day")]:
        cutoff = today - pd.Timedelta(days=window)
        window_rides = [r for r in rides if pd.to_datetime(r["start_time"]) >= cutoff]
        combined = pd.concat([pd.DataFrame(r["data"]) for r in window_rides if "power" in r["data"][0]], ignore_index=True)
        if not combined.empty:
            trends[label] = get_best_efforts(combined, durations)

    return trends
