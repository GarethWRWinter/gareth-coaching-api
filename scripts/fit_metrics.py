# scripts/fit_metrics.py
import numpy as np
from scripts.constants import FTP

def classify_power_zones(power_series):
    """
    Classify time spent in each power zone based on FTP.
    Returns a dict with time in seconds for each zone.
    """
    zones = {
        "Zone 1: Recovery": (0, 0.55 * FTP),
        "Zone 2: Endurance": (0.55 * FTP, 0.75 * FTP),
        "Zone 3: Tempo": (0.75 * FTP, 0.9 * FTP),
        "Zone 4: Threshold": (0.9 * FTP, 1.05 * FTP),
        "Zone 5: VO2max": (1.05 * FTP, 1.2 * FTP),
        "Zone 6: Anaerobic Capacity": (1.2 * FTP, 1.5 * FTP),
        "Zone 7: Neuromuscular Power": (1.5 * FTP, np.inf)
    }

    zone_times = {zone: 0 for zone in zones}

    for power in power_series:
        for zone, (low, high) in zones.items():
            if low <= power < high:
                zone_times[zone] += 1  # 1 second per entry

    # Logging for debugging
    print(f"⚡️ FTP: {FTP} watts")
    for zone, (low, high) in zones.items():
        print(f"⚡️ {zone}: {low:.1f}–{high:.1f} watts (seconds: {zone_times[zone]})")

    return zone_times

def convert_zone_times_to_minutes(zone_times):
    """
    Convert zone times from seconds to minutes.
    """
    return {zone: round(seconds / 60, 1) for zone, seconds in zone_times.items()}
