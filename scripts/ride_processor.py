import pandas as pd
from scripts.parse_fit import parse_fit_file
from scripts.time_in_zones import calculate_time_in_zones
from scripts.fit_metrics import calculate_np_if_vi
from scripts.ride_database import store_ride, get_all_rides_from_db, get_trend_data, get_power_trend_data, update_ftp_in_db
from scripts.constants import FTP

def process_latest_fit_file():
    fit_data = parse_fit_file()  # Fetch latest .fit file data as DataFrame
    power_data = fit_data["power"]

    # Calculate NP, IF, VI using Training Peaks method
    np, if_, vi = calculate_np_if_vi(power_data, FTP)

    # Calculate time in power zones
    power_zone_times = calculate_time_in_zones(power_data, FTP)

    # Build ride summary
    ride_summary = {
        "ride_id": fit_data["ride_id"],
        "start_time": fit_data["start_time"],
        "duration_sec": fit_data["duration_sec"],
        "distance_km": fit_data["distance_km"],
        "avg_power": fit_data["avg_power"],
        "max_power": fit_data["max_power"],
        "tss": fit_data["tss"],
        "total_work_kj": fit_data["total_work_kj"],
        "normalized_power": np,
        "intensity_factor": if_,
        "variability_index": vi,
        "power_zone_times": power_zone_times,
        "avg_hr": fit_data.get("avg_hr"),
        "max_hr": fit_data.get("max_hr"),
        "avg_cadence": fit_data.get("avg_cadence"),
        "max_cadence": fit_data.get("max_cadence"),
        "left_right_balance": fit_data.get("left_right_balance"),
    }

    # Save to DB
    store_ride(ride_summary)

    return ride_summary

def get_all_rides():
    return get_all_rides_from_db()

def get_trend_analysis():
    return get_trend_data()

def get_power_trends():
    return get_power_trend_data()

def detect_and_update_ftp():
    # Placeholder: Implement FTP auto-detection if needed
    return {"message": "No FTP updates detected."}
