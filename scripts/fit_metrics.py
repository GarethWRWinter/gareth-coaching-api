# scripts/fit_metrics.py

import pandas as pd
from typing import Dict
from scripts.zone_classification import classify_power_zones_absolute

def calculate_power_zones(power_data: pd.Series, ftp: float) -> Dict[str, Dict[str, float]]:
    """
    Classify time in zones dynamically based on FTP.

    Args:
        power_data: Pandas Series of power data (1 per second).
        ftp: Current FTP in watts.

    Returns:
        Dictionary with seconds, minutes, and total_seconds spent in each zone.
    """
    power_list = power_data.fillna(0).astype(int).tolist()
    zone_data = classify_power_zones_absolute(power_list, ftp)
    return zone_data

def calculate_ride_metrics(df: pd.DataFrame, ftp: float) -> Dict:
    """
    Calculate summary metrics for the ride.
    """
    ride_metrics = {
        "duration_sec": df.shape[0],
        "avg_power": df["power"].mean(),
        "max_power": df["power"].max(),
        "avg_hr": df["heart_rate"].mean() if "heart_rate" in df.columns else None,
        "max_hr": df["heart_rate"].max() if "heart_rate" in df.columns else None,
        "avg_cadence": df["cadence"].mean() if "cadence" in df.columns else None,
        "max_cadence": df["cadence"].max() if "cadence" in df.columns else None,
        "total_work_kj": (df["power"].sum() / 1000) if "power" in df.columns else 0
    }
    
    # Dynamically calculate power zones based on current FTP
    ride_metrics["power_zone_times"] = calculate_power_zones(df["power"], ftp)
    
    return ride_metrics
