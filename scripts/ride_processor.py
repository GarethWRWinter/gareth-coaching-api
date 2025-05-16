import os
import dropbox
from fitparse import FitFile
from datetime import datetime
from scripts.ride_database import store_ride_data
from scripts.fit_sanitizer import sanitize_fit_data
from scripts.fit_metrics import calculate_ride_metrics

def process_latest_fit_file(access_token: str):
    dbx = dropbox.Dropbox(access_token)
    folder_path = os.getenv("DROPBOX_FOLDER", "/WahooFitness")

    # List and sort .FIT files by latest modified
    files = dbx.files_list_folder(folder_path).entries
    fit_files = [f for f in files if f.name.endswith(".fit")]
    if not fit_files:
        raise Exception("No .FIT files found in Dropbox folder")

    latest_file = sorted(fit_files, key=lambda x: x.client_modified, reverse=True)[0]
    metadata, res = dbx.files_download(f"{folder_path}/{latest_file.name}")
    local_path = f"/tmp/{latest_file.name}"

    with open(local_path, "wb") as f:
        f.write(res.content)

    # Parse and sanitize FIT file
    fitfile = FitFile(local_path)
    fitfile.parse()
    sanitized = sanitize_fit_data(fitfile)

    # Calculate metrics
    summary = calculate_ride_metrics(sanitized)
    ride_id = summary["ride_id"]
    timestamp = datetime.fromisoformat(summary["timestamp"])

    # Store ride
    store_ride_data(ride_id, timestamp, summary["duration"], summary["avg_power"], summary["training_stress_score"])

    return {
        "ride_id": ride_id,
        "timestamp": summary["timestamp"],
        "summary": summary,
        "data": sanitized
    }
