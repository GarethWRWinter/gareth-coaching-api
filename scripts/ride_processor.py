# scripts/ride_processor.py

from datetime import datetime
from typing import Dict
from scripts.parse_fit import parse_fit
from scripts.fit_metrics import calculate_ride_metrics
from scripts.ride_database import store_ride
from scripts.sanitize import sanitize

def process_latest_fit_file(filepath: str, ftp: float) -> Dict:
    df = parse_fit(filepath)
    if df.empty:
        raise ValueError("No data found in FIT file.")
    ride_metrics = calculate_ride_metrics(df, ftp)
    ride_metrics = sanitize(ride_metrics)
    ride_id = f"{datetime.utcnow().strftime('%Y-%m-%dT%H%M%SZ')}-{filepath.split('/')[-1]}"
    ride_metrics["ride_id"] = ride_id
    store_ride(ride_metrics)
    return ride_metrics
