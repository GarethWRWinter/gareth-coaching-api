import os
import json
from scripts.parse_fit import parse_fit_file
from scripts.dropbox_fetch import fetch_latest_fit_file
from scripts.ride_database import save_ride_summary
from datetime import datetime

def process_latest_fit_file(access_token):
    local_path = fetch_latest_fit_file(access_token)
    parsed = parse_fit_file(local_path)

    ride_id = parsed["ride_id"]
    timestamp = parsed["records"][0]["timestamp"]
    duration = parsed["summary"]["duration"]
    avg_power = parsed["summary"]["avg_power"]
    tss = parsed["summary"].get("training_stress_score", 0)

    save_ride_summary(ride_id, timestamp, duration, avg_power, tss, json.dumps(parsed))
    return parsed
