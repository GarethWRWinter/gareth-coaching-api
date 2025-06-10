# scripts/time_in_zones.py

def calculate_power_zones(ftp: float) -> dict:
    """
    Calculate power zones based on FTP (Functional Threshold Power).
    Zones are returned as a dictionary with (lower_bound, upper_bound) in watts.
    """
    return {
        "Zone 1: Recovery": (0, 0.55 * ftp),
        "Zone 2: Endurance": (0.55 * ftp, 0.75 * ftp),
        "Zone 3: Tempo": (0.75 * ftp, 0.9 * ftp),
        "Zone 4: Threshold": (0.9 * ftp, 1.05 * ftp),
        "Zone 5: VO2max": (1.05 * ftp, 1.2 * ftp),
        "Zone 6: Anaerobic Capacity": (1.2 * ftp, 1.5 * ftp),
        "Zone 7: Neuromuscular Power": (1.5 * ftp, float("inf")),
    }
