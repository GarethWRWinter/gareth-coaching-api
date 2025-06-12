# scripts/ride_processor.py
from datetime import datetime
from typing import Dict
import os
import pandas as pd

from scripts.parse_fit import parse_fit
from scripts.fit_metrics import calculate_ride_metrics
from scripts.ride_database import store_ride, get_ride_history, RideDBError
from scripts.sanitize import sanitize

LATEST_FIT_PATH = os.getenv("LATEST_FIT_PATH", "/mnt/data/latest.fit")

def process_latest_fit_file(ftp: float) -> Dict:
    """
    Process the latest .FIT file using provided FTP.
    """
    filepath = LATEST_FIT_PATH
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"No FIT file at {filepath}")

    df = parse_fit(filepath)
    if df.empty:
        raise ValueError("No data found in FIT file.")

    ride_metrics = calculate_ride_metrics(df, ftp)
    ride_metrics = sanitize(ride_metrics)

    ride_id = f"{datetime.now().strftime('%Y-%m-%d-%H%M%S')}-{os.path.basename(filepath)}"
    ride_metrics['ride_id'] = ride_id

    store_ride(ride_metrics)
    return ride_metrics

def get_all_rides() -> list[dict]:
    try:
        return [r.to_dict() for r in get_ride_history()]
    except AttributeError:
        return [r for r in get_ride_history()]

