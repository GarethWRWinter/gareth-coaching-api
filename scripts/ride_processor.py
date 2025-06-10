import pandas as pd
from scripts.time_in_zones import calculate_power_zones, calculate_hr_zones
from scripts.ride_database import get_dynamic_ftp, store_ride
from scripts.parse_fit import parse_fit_file

def process_latest_fit_file(file_path: str):
    df = parse_fit_file(file_path)
    ftp = get_dynamic_ftp()

    power_zone_times = calculate_power_zones(df['power'], ftp)
    hr_zone_times = calculate_hr_zones(df['heart_rate'])

    ride_summary = {
        "ride_id": file_path.split("/")[-1],
        "start_time": pd.to_datetime(df['timestamp'].iloc[0]),
        "duration_sec": int((df['timestamp'].iloc[-1] - df['timestamp'].iloc[0]).total_seconds()),
        "avg_power": df['power'].mean(),
        "avg_hr": df['heart_rate'].mean(),
        "max_power": df['power'].max(),
        "max_hr": df['heart_rate'].max(),
        "tss": 0,  # Placeholder
        "normalized_power": 0,  # Placeholder
        "left_right_balance": None,
        "power_zone_times": power_zone_times,
        "hr_zone_times": hr_zone_times,
    }

    store_ride(ride_summary)
    return ride_summary
