def calculate_time_in_zones(power_series, zones):
    if power_series is None or len(power_series) == 0:
        return {zone: 0 for zone in zones.keys()}

    time_in_zones = {zone: 0 for zone in zones.keys()}

    for power in power_series:
        for zone, (low, high) in zones.items():
            if low <= power < high:
                time_in_zones[zone] += 1
                break
    return time_in_zones


def compute_time_in_power_zones(power_series, zones):
    return calculate_time_in_zones(power_series, zones)


def compute_time_in_hr_zones(hr_series):
    max_hr = 190
    hr_zones = {
        "Z1": (0, 0.60 * max_hr),
        "Z2": (0.60 * max_hr, 0.70 * max_hr),
        "Z3": (0.70 * max_hr, 0.80 * max_hr),
        "Z4": (0.80 * max_hr, 0.90 * max_hr),
        "Z5": (0.90 * max_hr, max_hr + 1),
    }

    time_in_zones = {zone: 0 for zone in hr_zones}
    for hr in hr_series:
        for zone, (low, high) in hr_zones.items():
            if low <= hr < high:
                time_in_zones[zone] += 1
                break
    return time_in_zones
