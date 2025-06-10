def calculate_power_zones(power_series, ftp):
    """
    Calculate time in each power zone based on dynamic FTP.
    Returns a dict with time spent in each zone.
    """
    zones = {
        'Zone 1: Recovery': (0, 0.55 * ftp),
        'Zone 2: Endurance': (0.55 * ftp, 0.75 * ftp),
        'Zone 3: Tempo': (0.75 * ftp, 0.90 * ftp),
        'Zone 4: Threshold': (0.90 * ftp, 1.05 * ftp),
        'Zone 5: VO2max': (1.05 * ftp, 1.20 * ftp),
        'Zone 6: Anaerobic Capacity': (1.20 * ftp, 1.50 * ftp),
        'Zone 7: Neuromuscular Power': (1.50 * ftp, 2000)
    }

    seconds = {}
    for zone, (low, high) in zones.items():
        seconds[zone] = power_series[(power_series >= low) & (power_series < high)].count()

    minutes = {zone: round(sec / 60.0, 2) for zone, sec in seconds.items()}

    return {
        'seconds': seconds,
        'minutes': minutes,
        'total_seconds': int(power_series.count())
    }
