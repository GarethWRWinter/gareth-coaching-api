import os
from scripts.dropbox_utils import (
    get_latest_fit_file_from_dropbox,
    list_fit_files_in_dropbox,
    download_fit_file_from_dropbox
)
from scripts.fit_parser import parse_fit_file
from scripts.fit_metrics import calculate_ride_metrics
from scripts.ride_database import store_ride, get_all_ride_summaries, get_ride_by_id
from scripts.sanitize import sanitize
from datetime import datetime

def process_latest_fit_file():
    fit_file_bytes, filename = get_latest_fit_file_from_dropbox()
    df = parse_fit_file(fit_file_bytes)
    summary = calculate_ride_metrics(df)
    store_ride(summary["ride_id"], df, summary)
    return sanitize(df.to_dict(orient="records")), sanitize(summary)

def backfill_all_rides():
    filenames = list_fit_files_in_dropbox()
    backfilled = 0
    skipped = 0

    for filename in filenames:
        ride_id = os.path.splitext(filename)[0]
        existing = get_ride_by_id(ride_id)
        if existing:
            skipped += 1
            continue

        try:
            fit_file_bytes = download_fit_file_from_dropbox(filename)
            df = parse_fit_file(fit_file_bytes)
            summary = calculate_ride_metrics(df)
            store_ride(summary["ride_id"], df, summary)
            backfilled += 1
        except Exception as e:
            print(f"Failed to process {filename}: {e}")
            continue

    return backfilled, skipped, backfilled + skipped

def get_all_ride_summaries(include_full_data=False):
    return get_all_ride_summaries(include_full_data=include_full_data)
