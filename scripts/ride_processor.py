import os
from scripts.fetch_fit_from_dropbox import get_latest_fit_file_from_dropbox, download_fit_file_from_dropbox
from scripts.fit_parser import parse_fit_file
from scripts.fit_metrics import calculate_ride_metrics
from scripts.ride_database import store_ride
from scripts.sanitize import sanitize

def process_latest_fit_file():
    # Get the latest .fit file from Dropbox
    access_token = os.getenv("DROPBOX_TOKEN")
    folder_path = os.getenv("DROPBOX_FOLDER")
    
    file_name = get_latest_fit_file_from_dropbox(access_token, folder_path)
    local_path = download_fit_file_from_dropbox(access_token, folder_path, file_name)

    # Parse raw fit file → dict records
    fit_records = parse_fit_file(local_path)

    # Calculate summary metrics from records
    ride_summary = calculate_ride_metrics(fit_records)

    # Store ride in DB
    store_ride(ride_summary)

    # Return full data to route (cleaned for JSON)
    return {
        "summary": sanitize(ride_summary),
        "records": sanitize(fit_records),
    }
