import numpy as np
from collections import defaultdict

def calculate_time_in_zones(data, ftp):
    zones = {
        "Z1": (0, 0.55 * ftp),
        "Z2": (0.55 * ftp, 0.75 * ftp),
        "Z3": (0.75 * ftp, 0.90 * ftp),
        "Z4": (0.90 * ftp, 1.05 * ftp),
        "Z5": (1.05 * ftp, 1.20 * ftp),
        "Z6": (1.20 * ftp, 1.50 * ftp),
        "Z7": (1.50 * ftp, float("inf")),
    }

    time_in_zones = defaultdict(float)

    for i in range(1, len(data)):
        power = data[i]["power"]
        duration = (data[i]["timestamp"] - data[i - 1]["timestamp"]).total_seconds()

        for zone, (lower, upper) in zones.items():
            if lower <= power < upper:
                time_in_zones[zone] += duration
                break

    # Convert to readable format
    return {
        zone: {
            "seconds": round(seconds),
            "minutes": round(seconds / 60, 1)
        }
        for zone, seconds in time_in_zones.items()
    }
