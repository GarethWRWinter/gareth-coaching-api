# scripts/ride_processor.py

import pandas as pd
from typing import Dict
from scripts.ride_database import get_ftp, store_ride
from scripts.time_in_zones import calculate_time_in_zones
import numpy as np

def process_latest_fit_file(filepath: str) -> dict:
    df = pd.read_pickle(filepath) if filepath.endswith(".pkl") else pd.read_csv(filepath)
    # Assume timestamp, power, heart_rate columns exist
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    zones_data = calculate_time_in_zones(df)

    ride_data = {
        "ride_id": filepath,
        "start_time": df["timestamp"].min().to_pydatetime(),
        "duration_sec": (df["timestamp"].iloc[-1] - df["timestamp"].iloc[0]).total_seconds(),
        "avg_power": float(df["power"].mean()),
        "max_power": float(df["power"].max()),
        "tss": 0.0,  # compute TSS separately or leave placeholder
        "total_work_kj": float(df["power"].sum() / 1000.0),
        "power_zone_times": zones_data["power"]["minutes"],
        "hr_zone_times": zones_data["heart_rate"]["minutes"]
    }

    store_ride(ride_data)
    return ride_data

def get_all_rides():
    from scripts.ride_database import get_all_rides as db_get
    return db_get()
