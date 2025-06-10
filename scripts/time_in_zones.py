# scripts/time_in_zones.py

import pandas as pd
from scripts.ride_database import get_ftp
from scripts.fit_metrics import classify_power_zones, convert_zone_times_to_minutes

# Define HR zones (percent of max HR — customize as needed)
HR_ZONES = {
    "Zone 1: Recovery": (0.50, 0.60),
    "Zone 2: Endurance": (0.61, 0.70),
    "Zone 3: Tempo": (0.71, 0.80),
    "Zone 4: Threshold": (0.81, 0.90),
    "Zone 5: VO2max": (0.91, 1.00)
}

def calculate_time_in_zones(df: pd.DataFrame) -> dict:
    """
    Returns power and HR zone time breakdowns (in seconds + minutes).
    """
    # sanitize data
    df = df.copy()
    df["power"] = pd.to_numeric(df.get("power", 0), errors="coerce").fillna(0)
    df["heart_rate"] = pd.to_numeric(df.get("heart_rate", 0), errors="coerce").fillna(0)

    # get dynamic FTP
    ftp = get_ftp()

    # power zones
    power_seconds = classify_power_zones(df["power"], ftp)
    power_minutes = convert_zone_times_to_minutes(power_seconds)

    # heart rate zones
    hr_seconds = {}
    total_samples = len(df)
    max_hr = df["heart_rate"].max() or 0

    for name, (low_p, high_p) in HR_ZONES.items():
        count = ((df["heart_rate"] / max_hr).between(low_p, high_p)).sum()
        hr_seconds[name] = int(count)

    hr_minutes = convert_zone_times_to_minutes(hr_seconds)

    return {
        "power": {"seconds": power_seconds, "minutes": power_minutes},
        "heart_rate": {"seconds": hr_seconds, "minutes": hr_minutes},
        "total_samples": total_samples
    }
