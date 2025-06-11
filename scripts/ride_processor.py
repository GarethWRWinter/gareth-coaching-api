from datetime import datetime
from typing import Dict
import pandas as pd

from scripts.parse_fit import parse_fit
from scripts.fit_metrics import calculate_ride_metrics
from scripts.ride_database import store_ride, RideStorageError
from scripts.sanitize import sanitize

def process_latest_fit_file(filepath: str, ftp: float) -> Dict:
    df = parse_fit(filepath)
    if df.empty:
        raise ValueError(f"No data in FIT file at {filepath}")

    metrics = calculate_ride_metrics(df, ftp)
    metrics = sanitize(metrics)

    ride_id = f"{datetime.utcnow():%Y-%m-%d-%H%M%S}-{filepath.split('/')[-1]}"
    metrics.update({
        "ride_id": ride_id,
        "processed_at": datetime.utcnow().isoformat()
    })

    try:
        store_ride(metrics)
    except RideStorageError as e:
        # log the specific error and propagate it
        raise RuntimeError(f"DB storage failed for ride_id={ride_id}: {e}") from e

    return metrics
