# scripts/time_in_zones.py
import pandas as pd
from scripts.constants import FTP
from scripts.fit_metrics import classify_power_zones, convert_zone_times_to_minutes

def compute_time_in_zones(df):
    """
    Compute time spent in each power zone from ride data.
    """
    # Clean power data
    df = df.copy()
    df["power"] = pd.to_numeric(df["power"], errors="coerce").fillna(0)

    # Logging FTP and data state
    print(f"⚡️ Using FTP: {FTP}")
    print(f"⚡️ Data points: {len(df)}")

    # Classify zones
    zone_times_sec = classify_power_zones(df["power"])

    # Convert to minutes
    zone_times_min = convert_zone_times_to_minutes(zone_times_sec)

    # Structure
    zone_data = {
        "seconds": zone_times_sec,
        "minutes": zone_times_min,
        "total_seconds": int(df.shape[0])
    }

    return zone_data
