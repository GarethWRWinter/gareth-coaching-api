def calculate_time_in_zones(power_series, zones):
    """
    Calculate time spent in each power zone.

    Args:
        power_series (list or iterable of int): Power values (watts)
        zones (dict): Power zone thresholds

    Returns:
        dict: Time in seconds spent in each zone
    """
    time_in_zone = {zone: 0 for zone in zones.keys()}

    for power in power_series:
        for zone, (low, high) in zones.items():
            if low <= power < high:
                time_in_zone[zone] += 1
                break

    return time_in_zone
