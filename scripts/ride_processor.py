import os
from scripts.dropbox_auth import refresh_dropbox_token
from scripts.fetch_fit_from_dropbox import get_latest_fit_file_from_dropbox, download_fit_file_from_dropbox
from scripts.fit_parser import parse_fit
from scripts.fit_metrics import calculate_ride_metrics
from scripts.ride_database import store_ride, get_all_ride_summaries, get_ride_by_id
from scripts.save_latest_ride_to_db import save_latest_ride_to_db
from scripts.backfill_from_dropbox import backfill_all_rides

def process_latest_fit_file():
    access_token = refresh_dropbox_token()
    folder_path, file_name, local_path = get_latest_fit_file_from_dropbox(access_token)
    download_fit_file_from_dropbox(access_token, folder_path, file_name, local_path)
    fit_data = parse_fit(local_path)
    ride_summary = calculate_ride_metrics(fit_data)
    save_latest_ride_to_db(ride_summary, fit_data)
    return ride_summary, fit_data
