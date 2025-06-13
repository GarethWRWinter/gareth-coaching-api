import os
from scripts.fetch_fit_from_dropbox import get_latest_fit_file_from_dropbox, download_fit_file_from_dropbox
from scripts.fit_parser import parse_fit_file
from scripts.fit_metrics import calculate_ride_metrics
from scripts.ride_database import store_ride, fetch_ride_by_id
from scripts.sanitize import sanitize


def process_latest_fit_file():
    access_token = os.getenv("DROPBOX_TOKEN")
    folder_path = os.getenv("DROPBOX_FOLDER")

    file_name = get_latest_fit_file_from_dropbox(access_token, folder_path)
    local_path = download_fit_file_from_dropbox(access_token, folder_path, file_name)

    fit_records = parse_fit_file(local_path)
    ride_summary = calculate_ride_metrics(fit_records)
    store_ride(ride_summary)

    return {
        "summary": sanitize(ride_summary),
        "records": sanitize(fit_records),
    }


def get_ride_by_id(ride_id: str):
    """
    Retrieve full ride data by ride_id from the database.
    """
    ride_data = fetch_ride_by_id(ride_id)
    if not ride_data:
        raise ValueError(f"Ride with ID '{ride_id}' not found.")
    return sanitize(ride_data)
