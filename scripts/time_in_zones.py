import pandas as pd
import numpy as np

def calculate_time_in_zones(power_series: pd.Series, ftp: float) -> dict:
    """
    Calculate time spent in each power zone (using 3s rolling average power).
    """
    # Calculate 3s rolling average power
    power_3s = power_series.rolling(window=3, center=True, min_periods=1).mean()

    # Define power zones based on % of FTP
    zones = {
        'Zone 1: Recovery': (0, 0.55),
        'Zone 2: Endurance': (0.56, 0.75),
        'Zone 3: Tempo': (0.76, 0.90),
        'Zone 4: Threshold': (0.91, 1.05),
        'Zone 5: VO2max': (1.06, 1.20),
        'Zone 6: Anaerobic Capacity': (1.21, 1.50),
        'Zone 7: Neuromuscular Power': (1.51, np.inf)
    }

    # Initialize time counters
    zone_seconds = {zone: 0 for zone in zones}

    # Iterate through power data to count seconds in each zone
    for power in power_3s:
        ratio = power / ftp if ftp > 0 else 0
        for zone, (lower, upper) in zones.items():
            if lower <= ratio <= upper:
                zone_seconds[zone] += 1
                break

    # Convert to minutes
    zone_minutes = {zone: round(seconds / 60, 2) for zone, seconds in zone_seconds.items()}

    return {
        'seconds': zone_seconds,
        'minutes': zone_minutes,
        'total_seconds': int(power_3s.count())
    }
