# scripts/fit_metrics.py
import numpy as np

def classify_power_zones(power_series, ftp):
    """
    Classify power data into power zones based on provided FTP.
    """
    zones = {
        "Zone 1: Recovery": (0, 0.55),
        "Zone 2: Endurance": (0.56, 0.75),
        "Zone 3: Tempo": (0.76, 0.90),
        "Zone 4: Threshold": (0.91, 1.05),
        "Zone 5: VO2max": (1.06, 1.20),
        "Zone 6: Anaerobic Capacity": (1.21, 1.50),
        "Zone 7: Neuromuscular Power": (1.51, np.inf)
    }

    time_in_zones = {zone: 0 for zone in zones}

    for power in power_series:
        if ftp == 0:
            continue  # Avoid division by zero
        ratio = power / ftp
        for zone, (low, high) in zones.items():
            if low <= ratio <= high:
                time_in_zones[zone] += 1
                break

    return time_in_zones

def convert_zone_times_to_minutes(zone_times):
    """
    Convert time in zones from seconds to minutes (1 second per data point).
    """
    zone_times_min = {zone: round(sec / 60, 2) for zone, sec in zone_times.items()}
    return zone_times_min
