import os
from dotenv import load_dotenv
from scripts.fetch_fit_from_dropbox import (
    get_latest_fit_file_from_dropbox,
    download_fit_file_from_dropbox
)
from scripts.parse_fit import parse_fit  # ✅ corrected function name
from scripts.fit_parser import calculate_ride_metrics
from scripts.ride_database import store_ride, get_all_ride_summaries, get_ride_by_id

load_dotenv()

DROPBOX_FOLDER = os.getenv("DROPBOX_FOLDER", "/Apps/WahooFitness")

def process_latest_fit_file():
    # Step 1: Get latest filename
    file_name = get_latest_fit_file_from_dropbox(DROPBOX_FOLDER)

    # Step 2: Download to temp location
    local_path = f"/tmp/{file_name}"
    download_fit_file_from_dropbox(DROPBOX_FOLDER, file_name, local_path)

    # Step 3: Parse FIT file into raw data
    df = parse_fit(local_path)

    # Step 4: Generate ride summary
    ride_summary = calculate_ride_metrics(df, file_name)

    # Step 5: Store both
    store_ride(ride_summary, df)

    return ride_summary, df

def backfill_all_rides():
    raise NotImplementedError("Backfill functionality is not implemented in this version.")
