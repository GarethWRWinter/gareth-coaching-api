import os
from datetime import datetime
from scripts.fetch_fit_from_dropbox import get_latest_fit_file_from_dropbox, download_fit_file_from_dropbox
from scripts.fit_parser import parse_fit_file
from scripts.ride_database import store_ride, get_all_ride_summaries, get_ride_by_id
from scripts.fit_metrics import calculate_ride_metrics


def process_latest_fit_file():
    """
    Downloads, parses, calculates, and stores the latest ride from Dropbox.
    Returns: summary (dict), data (list of dicts)
    """
    latest_file_path = get_latest_fit_file_from_dropbox()
    local_path = download_fit_file_from_dropbox(latest_file_path)

    df = parse_fit_file(local_path)
    summary, data = calculate_ride_metrics(df)

    store_ride(summary, data)
    return summary, data


def backfill_all_rides():
    """
    Backfills all available FIT files from Dropbox, skipping already-logged rides.
    """
    from scripts.fetch_and_parse import list_fit_files_in_dropbox
    existing_ids = {r['ride_id'] for r in get_all_ride_summaries()}

    all_files = list_fit_files_in_dropbox()
    processed = []

    for fit_path in all_files:
        ride_id = os.path.basename(fit_path).split(".")[0]
        if ride_id in existing_ids:
            continue

        local_path = download_fit_file_from_dropbox(fit_path)
        df = parse_fit_file(local_path)
        summary, data = calculate_ride_metrics(df)
        store_ride(summary, data)
        processed.append(summary["ride_id"])

    return {"backfilled_rides": processed}
