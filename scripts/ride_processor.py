# scripts/ride_processor.py

import os
from scripts.fetch_fit_from_dropbox import get_latest_fit_file_from_dropbox
from scripts.parse_fit import parse_fit_file
from scripts.fit_metrics import calculate_ride_metrics
from scripts.ride_database import store_ride, get_latest_ride, get_ride_by_id
from scripts.sanitize import sanitize


def process_latest_fit_file():
    try:
        print("🚴 Processing latest ride...")
        access_token = os.getenv("DROPBOX_TOKEN")
        dropbox_folder = os.getenv("DROPBOX_FOLDER", "/Apps/WahooFitness")
        ftp = int(os.getenv("FTP", "308"))  # use environment or default fallback

        print(f"📁 Dropbox Folder: {dropbox_folder}, FTP: {ftp}")
        folder_path, file_name, local_path = get_latest_fit_file_from_dropbox(
            access_token=access_token,
            folder_path=dropbox_folder,
            local_download_path="latest_ride.fit"
        )
        print(f"📂 Downloaded FIT file: {local_path}")

        fit_df = parse_fit_file(local_path)
        print(f"📊 Parsed FIT DataFrame with {len(fit_df)} rows")

        summary = calculate_ride_metrics(fit_df, ftp=ftp)
        print(f"📈 Calculated ride summary: {summary}")

        store_ride(summary, fit_df)
        print(f"💾 Ride stored in database")

        return sanitize(summary), sanitize(fit_df.to_dict(orient="records"))
    except Exception as e:
        print(f"❌ Failed to process latest ride: {e}")
        raise
