import os
from datetime import datetime
from typing import Dict
from scripts.parse_fit import parse_fit
from scripts.fit_metrics import calculate_ride_metrics
from scripts.ride_database import store_ride, get_ride_history
from scripts.sanitize import sanitize

def process_latest_fit_file(filepath: str) -> Dict:
    df = parse_fit(filepath)
    if df.empty:
        raise ValueError("No data found in FIT file.")

    ftp = int(os.getenv("FTP", "250"))
    ride_metrics = calculate_ride_metrics(df, ftp)
    ride_metrics["ftp_used"] = ftp
    ride_metrics["ride_id"] = f"{datetime.now().strftime('%Y-%m-%d-%H%M%S')}-{filepath.split('/')[-1]}"
    ride_metrics = sanitize(ride_metrics)

    store_ride(ride_metrics)
    return ride_metrics
