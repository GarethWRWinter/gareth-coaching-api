# scripts/ride_processor.py

from datetime import datetime
from typing import Dict, Optional
import pandas as pd

from scripts.parse_fit import parse_fit
from scripts.fit_metrics import calculate_ride_metrics
from scripts.ride_database import store_ride, RideStorageError
from scripts.sanitize import sanitize  # ✅ Sanitize to remove non-JSON types

def process_latest_ride(filepath: str, ftp: float) -> Dict:
    """
    Process the latest .FIT file: parse, calculate metrics, sanitize, store,
    and return a ride summary dict.
    """
    df = parse_fit(filepath)
    if df.empty:
        raise ValueError("No data found in FIT file.")

    ride_metrics = calculate_ride_metrics(df, ftp)
    ride_metrics = sanitize(ride_metrics)

    ride_id = f"{datetime.now().strftime('%Y-%m-%d-%H%M%S')}-{filepath.split('/')[-1]}"
    ride_metrics['ride_id'] = ride_id

    try:
        store_ride(ride_metrics)
    except RideStorageError as e:
        raise RuntimeError(f"Error saving ride: {e}")

    return ride_metrics

def get_ride_history():
    from scripts.ride_database import get_ride_history as _gh
    return _gh()

def get_trend_analysis():
    from scripts.trend_analysis import calculate_trend_metrics
    return calculate_trend_metrics()

def get_power_trends():
    from scripts.rolling_power import calculate_rolling_power_trends
    return calculate_rolling_power_trends()

def detect_and_update_ftp():
    from scripts.ftp_detection import detect_and_update_ftp
    return detect_and_update_ftp()
