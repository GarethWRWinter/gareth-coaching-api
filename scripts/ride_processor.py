from datetime import datetime
from typing import Dict
import os
import pandas as pd

from scripts.parse_fit import parse_fit
from scripts.fit_metrics import calculate_ride_metrics
from scripts.ride_database import store_ride, get_ride_history
from scripts.sanitize import sanitize

LATEST_FIT_PATH = os.getenv("LATEST_FIT_PATH", "/mnt/data/latest.fit")

def process_latest_fit_file(ftp: float) -> Dict:
    """
    Processes the latest .FIT ride file using the given FTP.
    Calculates metrics and stores in DB.
    """
    filepath = LATEST_FIT_PATH
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"No FIT file at {filepath}")

    df: pd.DataFrame = parse_fit(filepath)
    if df.empty:
        raise ValueError("No data found in FIT file.")

    metrics = calculate_ride_metrics(df, ftp)
    metrics = sanitize(metrics)

    ride_id = f"{datetime.now().strftime('%Y-%m-%d-%H%M%S')}-{os.path.basename(filepath)}"
    metrics["ride_id"] = ride_id

    store_ride(metrics)
    return metrics

def get_all_rides() -> list[dict]:
    """
    Retrieves all rides from DB.
    Ensures consistent list-of-dicts output.
    """
    rides = get_ride_history()
    results = []
    for r in rides:
        if hasattr(r, "to_dict"):
            results.append(r.to_dict())
        elif isinstance(r, dict):
            results.append(r)
        else:
            results.append(vars(r))
    return results
