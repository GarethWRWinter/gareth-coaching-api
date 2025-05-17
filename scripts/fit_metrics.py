# scripts/fit_metrics.py

import numpy as np
import pandas as pd
from scripts.calculate_power_zones import get_power_zones
from scripts.calculate_tss import calculate_tss

def calculate_time_in_zones(power_series: list, ftp: int) -> dict:
    power_zones = get_power_zones(ftp)
    zone_times = {zone: 0 for zone in power_zones.keys()}

    for power in power_series:
        for zone, (low, high) in power_zones.items():
            if low <= power < high:
                zone_times[zone] += 1
                break

    return {
        zone: {
            "seconds": round(seconds, 1),
            "minutes": round(seconds / 60.0, 2)
        }
        for zone, seconds in zone_times.items()
    }

def calculate_ride_metrics(raw_data, ftp: int) -> dict:
    # ✅ Safely convert list-of-dicts into DataFrame
    if isinstance(raw_data, list):
        df = pd.DataFrame(raw_data)
    elif isinstance(raw_data, pd.DataFrame):
        df = raw_data
    else:
        raise ValueError("Unsupported data type. Expected list or DataFrame.")

    if df.empty:
        raise ValueError("DataFrame is empty. No ride data to process.")

    start_time = df["timestamp"].iloc[0]
    end_time = df["timestamp"].iloc[-1]
    duration_sec = (end_time - start_time).total_seconds()

    avg_power = df["power"].mean()
    max_power = df["power"].max()
    avg_hr = df["heart_rate"].mean()
    max_hr = df["heart_rate"].max()
    avg_cadence = df["cadence"].mean()
    max_cadence = df["cadence"].max()

    total_work = (df["power"] * df["timestamp"].diff().dt.total_seconds().fillna(0)).sum()

    power_series = df["power"].tolist()
    tss = calculate_tss(power_series, ftp)
    time_in_zones = calculate_time_in_zones(power_series, ftp)

    return {
        "ride_id": str(start_time),
        "start_time": str(start_time),
        "end_time": str(end_time),
        "duration_sec": round(duration_sec),
        "avg_power": round(avg_power, 1),
        "max_power": int(max_power),
        "avg_heart_rate": round(avg_hr, 1),
        "max_heart_rate": int(max_hr),
        "avg_cadence": round(avg_cadence, 1),
        "max_cadence": int(max_cadence),
        "total_work": round(total_work, 1),
        "tss": round(tss, 1),
        "time_in_zones": time_in_zones
    }
