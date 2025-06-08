# scripts/time_in_zones.py
import pandas as pd
from scripts.constants import FTP
from scripts.fit_metrics import classify_power_zones, convert_zone_times_to_minutes

def calculate_time_in_zones(df, ftp=None):
    """
    Compute time spent in each power zone from ride data.
    If an FTP is provided, it uses it; else it falls back to the global constant.
    """
    df = df.copy()
    df["power"] = pd.to_numeric(df["power"], errors="coerce").fillna(0)

    # Use provided FTP or fallback
    ftp_to_use = ftp if ftp is not None else FTP
    print(f"[INFO] Using FTP: {ftp_to_use}")
    print(f"[INFO] Data points: {len(df)}")

    zone_times_sec = classify_power_zones(df["power"], ftp_to_use)
    zone_times_min = convert_zone_times_to_minutes(zone_times_sec)

    zone_data = {
        "seconds": zone_times_sec,
        "minutes": zone_times_min,
        "total_seconds": int(df.shape[0])
    }

    return zone_data
