# scripts/ride_processor.py

import os
from scripts.fetch_fit_from_dropbox import get_latest_fit_file_from_dropbox
from scripts.parse_fit import parse_fit_file
from scripts.sanitize import sanitize
from scripts.fit_metrics import calculate_ride_metrics
from scripts.ride_database import store_ride, get_ride_history, get_ride_by_id
from scripts.constants import FTP_DEFAULT

def process_latest_fit_file(access_token: str, ftp: float = FTP_DEFAULT):
    folder_path = os.getenv("DROPBOX_FOLDER")
    if not folder_path:
        raise EnvironmentError("DROPBOX_FOLDER not set in environment variables.")

    # Step 1: Download latest .fit file
    folder_path, file_name, local_path = get_latest_fit_file_from_dropbox(access_token, folder_path)

    # Step 2: Parse FIT data
    raw_data = parse_fit_file(local_path)

    # Step 3: Calculate ride metrics using provided FTP
    ride_metrics = calculate_ride_metrics(raw_data, ftp)

    # Step 4: Store in database
    store_ride(ride_metrics)

    # Step 5: Sanitize for API response
    return sanitize(ride_metrics), raw_data

def process_specific_ride(file_path: str, ftp: float = FTP_DEFAULT):
    raw_data = parse_fit_file(file_path)
    ride_metrics = calculate_ride_metrics(raw_data, ftp)
    store_ride(ride_metrics)
    return sanitize(ride_metrics), raw_data

def get_all_rides():
    return get_ride_history()

def get_ride_details(ride_id: str):
    return get_ride_by_id(ride_id)
