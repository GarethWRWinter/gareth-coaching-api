# scripts/time_in_zones.py
import pandas as pd
import logging
from scripts.constants import FTP

def calculate_time_in_zones(df, ftp=FTP):
    # 🟩 Log the FTP value being used
    logging.basicConfig(level=logging.INFO)
    logging.info(f"🟩 Using FTP: {ftp} watts for time-in-zones calculation.")

    # 🟩 Apply pandas best practice: ensure .loc for safe assignment
    df.loc[:, "power"] = pd.to_numeric(df["power"], errors="coerce").fillna(0)

    zones = {
        "Zone 1: Active Recovery": 0,
        "Zone 2: Endurance": 0,
        "Zone 3: Tempo": 0,
        "Zone 4: Threshold": 0,
        "Zone 5: VO2max": 0,
        "Zone 6: Anaerobic Capacity": 0,
        "Zone 7: Neuromuscular Power": 0,
    }

    for power in df["power"]:
        if power < 0.55 * ftp:
            zones["Zone 1: Active Recovery"] += 1
        elif power < 0.75 * ftp:
            zones["Zone 2: Endurance"] += 1
        elif power < 0.90 * ftp:
            zones["Zone 3: Tempo"] += 1
        elif power < 1.05 * ftp:
            zones["Zone 4: Threshold"] += 1
        elif power < 1.20 * ftp:
            zones["Zone 5: VO2max"] += 1
        elif power < 1.50 * ftp:
            zones["Zone 6: Anaerobic Capacity"] += 1
        else:
            zones["Zone 7: Neuromuscular Power"] += 1

    total_seconds = sum(zones.values())
    zone_minutes = {zone: round(seconds / 60, 2) for zone, seconds in zones.items()}

    # 🟩 Log calculated times in zones for deeper debugging
    logging.info(f"🟩 Calculated time in zones (seconds): {zones}")
    logging.info(f"🟩 Calculated time in zones (minutes): {zone_minutes}")

    return {
        "seconds": zones,
        "minutes": zone_minutes,
        "total_seconds": total_seconds,
    }
