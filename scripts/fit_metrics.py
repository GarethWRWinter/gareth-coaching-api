import numpy as np
import pandas as pd
from scripts.calculate_tss import calculate_tss
from scripts.calculate_power_zones import get_power_zones
from scripts.time_in_zones import calculate_time_in_zones
from scripts.constants import DEFAULT_FTP
from datetime import datetime

def calculate_ride_metrics(df: pd.DataFrame, ftp: int = DEFAULT_FTP) -> dict:
    df = df.copy()

    # Fallbacks
    start_time = df['timestamp'].min() if 'timestamp' in df else pd.Timestamp.now()
    ride_id = start_time.strftime("%Y%m%d_%H%M%S") if not pd.isna(start_time) else "unknown"

    # Compute metrics only if columns exist
    avg_power = round(df["power"].mean(), 2) if "power" in df else None
    max_power = int(df["power"].max()) if "power" in df else None
    avg_hr = round(df["heart_rate"].mean(), 1) if "heart_rate" in df else None
    max_hr = int(df["heart_rate"].max()) if "heart_rate" in df else None
    duration_sec = len(df)

    # ✅ Fix TSS unpacking
    try:
        tss_val, np_val, if_val = calculate_tss(df["power"], ftp)
        tss = round(tss_val, 2)
    except Exception as e:
        print(f"TSS calculation failed: {e}")
        tss = None

    # Zones
    try:
        zones = get_power_zones(ftp)
        time_in_zones = calculate_time_in_zones(df["power"], zones) if "power" in df else {}
        time_in_zone_minutes = {
            zone: round(seconds / 60, 1) for zone, seconds in time_in_zones.items()
        }
    except Exception as e:
        print(f"Zone analysis failed: {e}")
        time_in_zone_minutes = {}

    return {
        "ride_id": ride_id,
        "start_time": str(start_time),
        "duration_sec": duration_sec,
        "avg_power": avg_power,
        "max_power": max_power,
        "avg_hr": avg_hr,
        "max_hr": max_hr,
        "tss": tss,
        "time_in_zones_min": time_in_zone_minutes,
    }
