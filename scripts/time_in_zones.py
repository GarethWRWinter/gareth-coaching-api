def calculate_power_zones(power_series, ftp):
    zones = {
        "Zone 1: Recovery": (0, 0.55 * ftp),
        "Zone 2: Endurance": (0.55 * ftp, 0.75 * ftp),
        "Zone 3: Tempo": (0.75 * ftp, 0.9 * ftp),
        "Zone 4: Threshold": (0.9 * ftp, 1.05 * ftp),
        "Zone 5: VO2max": (1.05 * ftp, 1.2 * ftp),
        "Zone 6: Anaerobic Capacity": (1.2 * ftp, 1.5 * ftp),
        "Zone 7: Neuromuscular Power": (1.5 * ftp, float('inf'))
    }

    zone_times = {zone: 0 for zone in zones}
    for power in power_series:
        for zone, (lower, upper) in zones.items():
            if lower <= power < upper:
                zone_times[zone] += 1
                break

    total_seconds = sum(zone_times.values())
    zone_times_minutes = {zone: round(seconds / 60, 2) for zone, seconds in zone_times.items()}

    return {
        "seconds": zone_times,
        "minutes": zone_times_minutes,
        "total_seconds": total_seconds
    }

def calculate_hr_zones(hr_series):
    zones = {
        "Zone 1": (0, 110),
        "Zone 2": (110, 130),
        "Zone 3": (130, 150),
        "Zone 4": (150, 170),
        "Zone 5": (170, 190),
        "Zone 6": (190, 210)
    }

    zone_times = {zone: 0 for zone in zones}
    for hr in hr_series:
        for zone, (lower, upper) in zones.items():
            if lower <= hr < upper:
                zone_times[zone] += 1
                break

    total_seconds = sum(zone_times.values())
    zone_times_minutes = {zone: round(seconds / 60, 2) for zone, seconds in zone_times.items()}

    return {
        "seconds": zone_times,
        "minutes": zone_times_minutes,
        "total_seconds": total_seconds
    }
