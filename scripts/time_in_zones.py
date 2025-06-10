def calculate_time_in_zones(power_data, ftp):
    zones = {
        "Zone 1: Recovery": (0, 0.55 * ftp),
        "Zone 2: Endurance": (0.55 * ftp, 0.75 * ftp),
        "Zone 3: Tempo": (0.75 * ftp, 0.9 * ftp),
        "Zone 4: Threshold": (0.9 * ftp, 1.05 * ftp),
        "Zone 5: VO2max": (1.05 * ftp, 1.2 * ftp),
        "Zone 6: Anaerobic Capacity": (1.2 * ftp, 1.5 * ftp),
        "Zone 7: Neuromuscular Power": (1.5 * ftp, float("inf")),
    }

    zone_seconds = {zone: 0 for zone in zones}

    for power in power_data:
        for zone, (lower, upper) in zones.items():
            if lower <= power < upper:
                zone_seconds[zone] += 1
                break

    # Convert to minutes
    zone_minutes = {zone: round(sec / 60.0, 2) for zone, sec in zone_seconds.items()}

    return {
        "seconds": zone_seconds,
        "minutes": zone_minutes,
        "total_seconds": sum(zone_seconds.values()),
    }
