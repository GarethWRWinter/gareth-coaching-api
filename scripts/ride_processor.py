# scripts/ride_processor.py

import os
from scripts.fetch_fit_from_dropbox import get_latest_fit_file_from_dropbox
from scripts.parse_fit import parse_fit_file
from scripts.fit_metrics import calculate_ride_metrics
from scripts.ride_database import store_ride, get_latest_ride, get_ride_by_id
from scripts.sanitize import sanitize


def process_latest_fit_file(ftp: int):
    """Fetches, parses, analyzes, and stores the latest FIT file ride."""
    access_token = os.getenv("DROPBOX_TOKEN")
    dropbox_folder = os.getenv("DROPBOX_FOLDER", "/Apps/WahooFitness")

    folder_path, file_name, local_path = get_latest_fit_file_from_dropbox(
        access_token=access_token,
        folder_path=dropbox_folder,
        local_download_path="latest_ride.fit"
    )

    fit_df = parse_fit_file(local_path)

    summary = calculate_ride_metrics(fit_df, ftp=ftp)

    store_ride(summary, fit_df)

    return sanitize(summary), sanitize(fit_df.to_dict(orient="records"))


def get_latest_ride_summary():
    return get_latest_ride()


def get_ride_by_id_from_db(ride_id):
    return get_ride_by_id(ride_id)
