from scripts.fetch_fit_from_dropbox import get_latest_fit_file_from_dropbox
from scripts.fit_parser import calculate_ride_metrics
from scripts.ride_database import store_ride
from scripts.constants import FTP
import pandas as pd
import fitparse
from datetime import datetime
import numpy as np


def process_latest_fit_file(access_token):
    file_name, local_path = get_latest_fit_file_from_dropbox(access_token)
    if not file_name or not local_path:
        return None

    fitfile = fitparse.FitFile(local_path)
    records = []
    for record in fitfile.get_messages("record"):
        record_data = {}
        for field in record:
            record_data[field.name] = field.value
        records.append(record_data)

    df = pd.DataFrame(records)
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"])

    print(f"[INFO] Using FTP (Functional Threshold Power): {FTP} watts")
    metrics = calculate_ride_metrics(df, FTP)

    ride_data = {
        "ride_id": file_name,
        "start_time": df["timestamp"].min().to_pydatetime() if "timestamp" in df.columns else datetime.utcnow(),
        "duration_sec": metrics["duration_seconds"],
        "distance_km": metrics.get("distance_km", 0),
        "avg_power": metrics["average_power"],
        "max_power": metrics["max_power"],
        "tss": metrics["tss"],
        "total_work_kj": metrics.get("total_work_kj", 0),
        "power_zone_times": metrics["zones"],
    }

    # Convert NumPy floats to native floats
    for k, v in ride_data.items():
        if isinstance(v, np.generic):
            ride_data[k] = float(v)

    store_ride(ride_data)

    return ride_data


def get_all_rides():  # ✅ Renamed from get_all_ride_summaries to get_all_rides
    from scripts.ride_database import get_all_rides as db_get_all_rides

    rides = db_get_all_rides()
    return rides
