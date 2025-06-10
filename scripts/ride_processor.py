import pandas as pd
from typing import Dict
from scripts.ride_database import get_dynamic_ftp
from scripts.time_in_zones import calculate_power_zones
from scripts.parse_fit import parse_fit_file


def process_ride_data(df: pd.DataFrame) -> Dict:
    """
    Process the parsed ride data, calculate zones, and prepare summary dict.
    """
    ftp = get_dynamic_ftp()
    duration_sec = (df['timestamp'].iloc[-1] - df['timestamp'].iloc[0]).total_seconds()
    avg_power = df['power'].mean()
    max_power = df['power'].max()
    total_work_kj = (df['power'].sum() * 1.0) / 1000.0

    power_zone_times = calculate_power_zones(df['power'], ftp)

    return {
        'duration_sec': duration_sec,
        'avg_power': avg_power,
        'max_power': max_power,
        'total_work_kj': total_work_kj,
        'power_zone_times': power_zone_times
    }


def process_latest_fit_file(filepath: str) -> Dict:
    """
    Parse the latest FIT file and process the data.
    """
    df = parse_fit_file(filepath)
    return process_ride_data(df)
