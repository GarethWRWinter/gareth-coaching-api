# scripts/ride_processor.py

from scripts.fetch_fit_from_dropbox import get_latest_fit_file_from_dropbox
from scripts.fit_parser import calculate_ride_metrics
from scripts.ride_database import store_ride
import pandas as pd
import fitparse
import os
from datetime import datetime

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

    ftp = 250  # Default FTP
    metrics = calculate_ride_metrics(df, ftp)

    # Prepare data for Postgres
    ride_data = {
        "ride_id": file_name,
        "start_time": df["timestamp"].min().to_pydatetime() if "timestamp" in df.columns else datetime.utcnow(),
        "duration_sec": metrics["duration_seconds"],
        "distance_km": metrics.get("distance_km", 0),
        "avg_power": metrics["average_power"],
        "avg_hr": metrics.get("average_hr", 0),
        "avg_cadence": metrics.get("average_cadence", 0),
        "max_power": metrics["max_power"],
        "max_hr": metrics.get("max_hr", 0),
        "max_cadence": metrics.get("max_cadence", 0),
        "total_work_kj": metrics.get("total_work_kj", 0),
        "tss": metrics["tss"],
        "left_right_balance": metrics.get("left_right_balance", None),
        "power_zone_times": metrics["zones"]
    }

    # Store the ride in Postgres
    store_ride(ride_data)

    return {
        "file_name": file_name,
        "metrics": metrics,
        "records_count": len(df),
    }

def get_all_ride_summaries():
    from scripts.ride_database import get_all_rides

    rides = get_all_rides()
    ride_summaries = []
    for ride in rides:
        summary = {
            "id": ride.id,
            "ride_id": ride.ride_id,
            "start_time": ride.start_time.isoformat() if ride.start_time else None,
            "duration_sec": ride.duration_sec,
            "distance_km": ride.distance_km,
            "avg_power": ride.avg_power,
            "max_power": ride.max_power,
            "tss": ride.tss,
            "total_work_kj": ride.total_work_kj,
            "power_zone_times": ride.power_zone_times,
        }
        ride_summaries.append(summary)
    return ride_summaries
