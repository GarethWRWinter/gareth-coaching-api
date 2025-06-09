# scripts/fit_metrics.py
import numpy as np

def classify_power_zones(power_series, ftp):
    """
    Classify power data into power zones based on provided FTP.
    Ensures every second is assigned to a zone.
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
            zone = "Zone 1: Recovery"  # fallback for FTP=0
        else:
            ratio = power / ftp
            zone_found = False
            for zone, (low, high) in zones.items():
                if low <= ratio <= high:
                    time_in_zones[zone] += 1
                    zone_found = True
                    break
            if not zone_found:
                # If somehow not found, assign to Zone 1 as safe fallback
                time_in_zones["Zone 1: Recovery"] += 1

    return time_in_zones

def convert_zone_times_to_minutes(zone_times):
    """
    Convert time in zones from seconds to minutes (1 second per data point).
    """
    zone_times_min = {zone: round(sec / 60, 2) for zone, sec in zone_times.items()}
    return zone_times_min
