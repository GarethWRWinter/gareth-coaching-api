from datetime import datetime
import os
from scripts.parse_fit import parse_fit
from scripts.fit_metrics import calculate_ride_metrics
from scripts.ride_database import store_ride, get_ride_history
from scripts.sanitize import sanitize

def process_latest_fit_file(ftp: int):
    filepath = "/mnt/data/latest.fit"
    df = parse_fit(filepath)
    if df.empty:
        raise ValueError("No data found in FIT file.")

    ride_metrics = calculate_ride_metrics(df, ftp)
    ride_metrics = sanitize(ride_metrics)

    ride_id = f"{datetime.now().strftime('%Y-%m-%d-%H%M%S')}-latest"
    ride_metrics["ride_id"] = ride_id
    ride_metrics["ftp_used"] = ftp

    store_ride(ride_metrics)
    return ride_metrics

def get_all_rides():
    return get_ride_history()
