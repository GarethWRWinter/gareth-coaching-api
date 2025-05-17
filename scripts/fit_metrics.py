# scripts/fit_metrics.py

import pandas as pd
from scripts.calculate_tss import calculate_tss
from scripts.time_in_zones import calculate_time_in_zones
from scripts.calculate_power_zones import get_power_zones
from scripts.constants import FTP

def generate_ride_summary(df: pd.DataFrame) -> dict:
    if df.empty:
        raise ValueError("DataFrame is empty. Cannot generate summary.")

    # Drop rows with missing timestamps
    df = df.dropna(subset=["timestamp"])

    start_time = df["timestamp"].min()
    end_time = df["timestamp"].max()
    total_duration_sec = (end_time - start_time).total_seconds()

    avg_power = df["power"].mean()
    max_power = df["power"].max()

    avg_heart_rate = df["heart_rate"].mean() if "heart_rate" in df.columns else None
    max_heart_rate = df["heart_rate"].max() if "heart_rate" in df.columns else None

    avg_cadence = df["cadence"].mean() if "cadence" in df.columns else None
    max_cadence = df["cadence"].max() if "cadence" in df.columns else None

    distance_km = df["distance"].iloc[-1] / 1000 if "distance" in df.columns else None
    total_work = (df["power"] * (df["timestamp"].diff().dt.total_seconds().fillna(0))).sum() if "power" in df.columns else 0
    tss_score = calculate_tss(df, FTP) if "power" in df.columns else 0
    time_in_zones = calculate_time_in_zones(df, FTP)

    summary = {
        "ride_id": start_time.isoformat(),
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "duration_sec": int(total_duration_sec),
        "distance_km": round(distance_km, 2) if distance_km else None,
        "avg_power": round(avg_power, 1) if avg_power else 0,
        "max_power": int(max_power) if max_power else 0,
        "avg_heart_rate": round(avg_heart_rate, 1) if avg_heart_rate else None,
        "max_heart_rate": int(max_heart_rate) if max_heart_rate else None,
        "avg_cadence": round(avg_cadence, 1) if avg_cadence else None,
        "max_cadence": int(max_cadence) if max_cadence else None,
        "total_work": round(total_work, 2),
        "tss": round(tss_score, 1),
        "time_in_zones": time_in_zones
    }

    return summary
