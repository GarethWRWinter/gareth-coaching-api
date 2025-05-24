# scripts/calculate_power_zones.py

def calculate_power_zones(power_series, ftp):
    zones = {
        "Z1": (0, 0.55 * ftp),
        "Z2": (0.55 * ftp, 0.75 * ftp),
        "Z3": (0.75 * ftp, 0.9 * ftp),
        "Z4": (0.9 * ftp, 1.05 * ftp),
        "Z5": (1.05 * ftp, 1.2 * ftp),
        "Z6": (1.2 * ftp, 1.5 * ftp),
        "Z7": (1.5 * ftp, float("inf"))
    }

    zone_counts = {zone: 0 for zone in zones}
    for power in power_series:
        for zone, (low, high) in zones.items():
            if low <= power < high:
                zone_counts[zone] += 1
                break

    return {zone: seconds for zone, seconds in zone_counts.items()}


def get_power_zones(ftp):
    return {
        "Z1": (0, 0.55 * ftp),
        "Z2": (0.55 * ftp, 0.75 * ftp),
        "Z3": (0.75 * ftp, 0.9 * ftp),
        "Z4": (0.9 * ftp, 1.05 * ftp),
        "Z5": (1.05 * ftp, 1.2 * ftp),
        "Z6": (1.2 * ftp, 1.5 * ftp),
        "Z7": (1.5 * ftp, float("inf"))
    }
