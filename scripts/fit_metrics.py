import pandas as pd
from typing import Dict
from scripts.zone_classification import classify_power_zones_absolute
import numpy as np

def calculate_power_zones(power_data: pd.Series, ftp: float) -> Dict[str, Dict[str, float]]:
    """
    Classify time in zones dynamically based on FTP.
    """
    power_list = power_data.fillna(0).astype(int).tolist()
    zone_data = classify_power_zones_absolute(power_list, ftp)
    return zone_data

def calculate_ride_metrics(df: pd.DataFrame, ftp: float) -> Dict:
    """
    Calculate summary metrics for the ride, including normalized power, TSS, and more.
    """
    ride_metrics = {
        "duration_sec": df.shape[0],
        "avg_power": df["power"].mean() if "power" in df.columns else None,
        "max_power": df["power"].max() if "power" in df.columns else None,
        "avg_hr": df["heart_rate"].mean() if "heart_rate" in df.columns else None,
        "max_hr": df["heart_rate"].max() if "heart_rate" in df.columns else None,
        "avg_cadence": df["cadence"].mean() if "cadence" in df.columns else None,
        "max_cadence": df["cadence"].max() if "cadence" in df.columns else None,
        "total_work_kj": (df["power"].sum() / 1000) if "power" in df.columns else 0,
        "left_right_balance": df["left_right_balance"].mean() if "left_right_balance" in df.columns else None,
    }

    # Start time
    ride_metrics["start_time"] = str(df.iloc[0]["timestamp"]) if "timestamp" in df.columns else None

    # Distance in km (from last record)
    if "distance" in df.columns and not df["distance"].isnull().all():
        ride_metrics["distance_km"] = df["distance"].iloc[-1] / 1000
    else:
        ride_metrics["distance_km"] = None

    # Normalized power
    if "power" in df.columns and not df["power"].isnull().all():
        rolling_30s = df["power"].rolling(window=30, min_periods=1).mean()
        norm_power = (rolling_30s ** 4).mean() ** (1/4)
        ride_metrics["normalized_power"] = norm_power
    else:
        ride_metrics["normalized_power"] = None

    # TSS calculation
    if ride_metrics["normalized_power"] and ftp:
        intensity_factor = ride_metrics["normalized_power"] / ftp
        duration_hr = ride_metrics["duration_sec"] / 3600
        tss = (duration_hr * ride_metrics["normalized_power"] * intensity_factor) / ftp * 100
        ride_metrics["tss"] = tss
    else:
        ride_metrics["tss"] = None

    # Power zones
    ride_metrics["power_zone_times"] = calculate_power_zones(df["power"], ftp) if "power" in df.columns else {}

    return ride_metrics
