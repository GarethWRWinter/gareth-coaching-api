from datetime import datetime
from typing import Dict, Optional
import pandas as pd

from scripts.parse_fit import parse_fit
from scripts.fit_metrics import calculate_ride_metrics
from scripts.ride_database import store_ride
from scripts.sanitize import sanitize  # ✅ Import the sanitize function

def process_latest_fit_file(filepath: str, ftp: float) -> Dict:
    """
    Process a .FIT file and compute ride metrics.
    Returns a dictionary with ride summary data.
    """
    df = parse_fit(filepath)
    if df.empty:
        raise ValueError("No data found in FIT file.")

    ride_metrics = calculate_ride_metrics(df, ftp)

    # ✅ Sanitize to ensure no np types in the dictionary
    ride_metrics = sanitize(ride_metrics)

    ride_id = f"{datetime.now().strftime('%Y-%m-%d-%H%M%S')}-{filepath.split('/')[-1]}"
    ride_metrics['ride_id'] = ride_id

    # Store ride in the database
    store_ride(ride_metrics)

    return ride_metrics

def get_all_rides():
    from scripts.ride_database import get_ride_history
    return get_ride_history()

def get_trend_analysis():
    from scripts.trend_analysis import calculate_trend_metrics
    return calculate_trend_metrics()

def get_power_trends():
    from scripts.rolling_power import calculate_rolling_power_trends
    return calculate_rolling_power_trends()

def detect_and_update_ftp():
    from scripts.ftp_detection import detect_and_update_ftp
    return detect_and_update_ftp()
