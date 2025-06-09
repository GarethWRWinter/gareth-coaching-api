# scripts/fit_metrics.py

import pandas as pd
from typing import Dict
from scripts.zone_classification import classify_power_zones_absolute

def calculate_power_zones(power_data: pd.Series, ftp: float) -> Dict[str, Dict[str, float]]:
    """
    Classify time in zones based on absolute wattage boundaries (like TrainingPeaks).

    Args:
        power_data: Pandas Series of power data (1 per second).
        ftp: Functional Threshold Power (used to calculate zone boundaries).

    Returns:
        Dictionary with seconds, minutes, and total_seconds spent in each zone.
    """
    # Example absolute boundaries for FTP = 308W
    zone_boundaries = [
        {"name": "Zone 1: Recovery", "min_watts": 0, "max_watts": 177},
        {"name": "Zone 2: Endurance", "min_watts": 178, "max_watts": 241},
        {"name": "Zone 3: Tempo", "min_watts": 242, "max_watts": 288},
        {"name": "Zone 4: Threshold", "min_watts": 289, "max_watts": 336},
        {"name": "Zone 5: VO2max", "min_watts": 337, "max_watts": 384},
        {"name": "Zone 6: Anaerobic Capacity", "min_watts": 385, "max_watts": 2000}
    ]
    
    # Convert power data to a list
    power_list = power_data.fillna(0).astype(int).tolist()
    
    # Use the new absolute classification logic
    zone_data = classify_power_zones_absolute(power_list, zone_boundaries)
    
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
        "total_work_kj": (df["power"].sum() * 1 / 1000) if "power" in df.columns else 0
    }
    
    # Calculate power zones
    ride_metrics["power_zone_times"] = calculate_power_zones(df["power"], ftp)
    
    return ride_metrics
