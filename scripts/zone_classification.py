# scripts/zone_classification.py

from typing import Dict, List

def classify_power_zones_absolute(power_data: List[int], zone_boundaries: List[Dict[str, float]]) -> Dict[str, Dict[str, float]]:
    """
    Classify time in zones based on absolute wattage boundaries.

    Args:
        power_data: List of power data points (1 per second).
        zone_boundaries: List of zone dicts with keys: name, min_watts, max_watts.

    Returns:
        Dictionary with seconds, minutes, and total_seconds spent in each zone.
    """
    zone_seconds = {zone['name']: 0 for zone in zone_boundaries}
    
    for power in power_data:
        assigned = False
        for zone in zone_boundaries:
            if zone['min_watts'] <= power <= zone['max_watts']:
                zone_seconds[zone['name']] += 1
                assigned = True
                break
        if not assigned:
            # If no zone matched (e.g. above highest zone), count as "Neuromuscular Power" (if using absolute zones)
            pass  # Or handle as needed

    total_seconds = sum(zone_seconds.values())
    zone_minutes = {zone: round(sec / 60, 2) for zone, sec in zone_seconds.items()}
    
    return {
        "seconds": zone_seconds,
        "minutes": zone_minutes,
        "total_seconds": total_seconds
    }

# Example usage
if __name__ == "__main__":
    # Dummy power data (replace with real data)
    power_data = [100, 250, 320, 360, 280, 310, 350, 370, 380, 290, 300]
    
    # TrainingPeaks absolute watt boundaries (example for your FTP 308W)
    zone_boundaries = [
        {"name": "Zone 1: Recovery", "min_watts": 0, "max_watts": 177},
        {"name": "Zone 2: Endurance", "min_watts": 178, "max_watts": 241},
        {"name": "Zone 3: Tempo", "min_watts": 242, "max_watts": 288},
        {"name": "Zone 4: Threshold", "min_watts": 289, "max_watts": 336},
        {"name": "Zone 5: VO2max", "min_watts": 337, "max_watts": 384},
        {"name": "Zone 6: Anaerobic Capacity", "min_watts": 385, "max_watts": 2000}  # Upper limit as needed
    ]
    
    result = classify_power_zones_absolute(power_data, zone_boundaries)
    print(result)
