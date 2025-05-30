# scripts/ride_processor.py

import os
from scripts.fetch_fit_from_dropbox import get_latest_fit_file_from_dropbox, list_fit_files_in_dropbox, download_fit_file_from_dropbox
from scripts.fit_parser import parse_fit_file
from scripts.ride_database import get_all_rides, get_ride


def process_latest_fit_file(access_token: str):
    folder_path = os.getenv("DROPBOX_FOLDER", "/WahooFitness")
    file_name, local_path = get_latest_fit_file_from_dropbox(access_token, folder_path)

    if file_name:
        data_df = parse_fit_file(local_path)
        if data_df is not None and not data_df.empty:
            return data_df
        else:
            raise ValueError("Parsed FIT file is empty or invalid")
    else:
        raise FileNotFoundError("No FIT file found in Dropbox")


def backfill_all_rides(access_token: str):
    folder_path = os.getenv("DROPBOX_FOLDER", "/WahooFitness")
    file_list = list_fit_files_in_dropbox(access_token, folder_path)

    processed_files = []
    for file in file_list:
        local_path = download_fit_file_from_dropbox(access_token, folder_path, file)
        data_df = parse_fit_file(local_path)
        if data_df is not None and not data_df.empty:
            processed_files.append(file)

    return processed_files


def get_all_ride_summaries():
    return get_all_rides()


def get_ride_by_id(ride_id: str):
    return get_ride(ride_id)
