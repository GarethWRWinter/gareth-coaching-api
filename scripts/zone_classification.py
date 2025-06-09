# scripts/zone_classification.py

from typing import Dict, List

def get_zone_boundaries_from_ftp(ftp: float) -> List[Dict[str, float]]:
    """
    Calculate zone boundaries dynamically based on FTP.

    Args:
        ftp: Functional Threshold Power in watts.

    Returns:
        List of zones with absolute wattage min and max boundaries.
    """
    return [
        {"name": "Zone 1: Recovery", "min_watts": 0, "max_watts": round(ftp * 0.55)},
        {"name": "Zone 2: Endurance", "min_watts": round(ftp * 0.56), "max_watts": round(ftp * 0.75)},
        {"name": "Zone 3: Tempo", "min_watts": round(ftp * 0.76), "max_watts": round(ftp * 0.90)},
        {"name": "Zone 4: Threshold", "min_watts": round(ftp * 0.91), "max_watts": round(ftp * 1.05)},
        {"name": "Zone 5: VO2max", "min_watts": round(ftp * 1.06), "max_watts": round(ftp * 1.20)},
        {"name": "Zone 6: Anaerobic Capacity", "min_watts": round(ftp * 1.21), "max_watts": 2000}
    ]

def classify_power_zones_absolute(power_data: List[int], ftp: float) -> Dict[str, Dict[str, float]]:
    """
    Classify time in zones using dynamically calculated zone boundaries.

    Args:
        power_data: List of power data points (1 per second).
        ftp: Functional Threshold Power in watts.

    Returns:
        Dictionary with seconds, minutes, and total_seconds spent in each zone.
    """
    zone_boundaries = get_zone_boundaries_from_ftp(ftp)
    zone_seconds = {zone['name']: 0 for zone in zone_boundaries}
    
    for power in power_data:
        assigned = False
        for zone in zone_boundaries:
            if zone['min_watts'] <= power <= zone['max_watts']:
                zone_seconds[zone['name']] += 1
                assigned = True
                break
        if not assigned:
            pass

    total_seconds = sum(zone_seconds.values())
    zone_minutes = {zone: round(sec / 60, 2) for zone, sec in zone_seconds.items()}
    
    return {
        "seconds": zone_seconds,
        "minutes": zone_minutes,
        "total_seconds": total_seconds
    }
