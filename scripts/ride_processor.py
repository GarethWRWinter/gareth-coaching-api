# scripts/ride_processor.py

import os
import uuid
from datetime import datetime
from scripts.fetch_fit_from_dropbox import get_latest_fit_file_from_dropbox, download_fit_file_from_dropbox
from scripts.parse_fit import parse_fit_file
from scripts.fit_metrics import calculate_ride_metrics
from scripts.sanitize import sanitize
from scripts.ride_database import store_ride, get_ride_by_id

def process_latest_fit_file(access_token: str, ftp: int):
    folder_path = os.getenv("DROPBOX_FOLDER", "/Apps/WahooFitness")
    file_name = get_latest_fit_file_from_dropbox(access_token, folder_path)
    local_path = download_fit_file_from_dropbox(access_token, folder_path, file_name)

    ride_id = str(uuid.uuid4())
    fit_data = parse_fit_file(local_path)
    ride_summary, second_by_second = calculate_ride_metrics(fit_data, ftp)
    ride_summary["ride_id"] = ride_id
    ride_summary["file_name"] = file_name
    ride_summary["timestamp"] = datetime.now().isoformat()

    store_ride(ride_id, ride_summary, second_by_second)
    return sanitize(ride_summary), sanitize(second_by_second)


def process_specific_fit_file(local_path: str, ftp: int, file_name: str = "manual_upload.fit"):
    ride_id = str(uuid.uuid4())
    fit_data = parse_fit_file(local_path)
    ride_summary, second_by_second = calculate_ride_metrics(fit_data, ftp)
    ride_summary["ride_id"] = ride_id
    ride_summary["file_name"] = file_name
    ride_summary["timestamp"] = datetime.now().isoformat()

    store_ride(ride_id, ride_summary, second_by_second)
    return sanitize(ride_summary), sanitize(second_by_second)


def get_ride_details(ride_id: str):
    summary, data = get_ride_by_id(ride_id)
    return sanitize(summary), sanitize(data)
