# scripts/backfill_ride_history.py

import os
import time
from scripts.dropbox_utils import list_fit_files_in_folder, download_file
from scripts.parse_fit_to_df import parse_fit_file_to_dataframe
from scripts.sanitize import sanitize_fit_data
from scripts.fit_metrics import generate_ride_summary
from scripts.ride_database import save_ride_summary
from scripts.dropbox_auth import refresh_dropbox_token

DROPBOX_FOLDER = os.getenv("DROPBOX_FOLDER", "/Apps/WahooFitness")


def backfill_all_rides():
    access_token = refresh_dropbox_token()
    file_paths = list_fit_files_in_folder(access_token)

    print(f"\n🧠 Found {len(file_paths)} FIT files in Dropbox folder '{DROPBOX_FOLDER}'\n")

    for path in sorted(file_paths):
        filename = path.split("/")[-1]
        print(f"📥 Downloading: {filename}")

        try:
            download_file(access_token, path, "temp.fit")
            df = parse_fit_file_to_dataframe("temp.fit")
            df = sanitize_fit_data(df)
            summary = generate_ride_summary(df)
            save_ride_summary(summary)
            print(f"✅ Saved ride: {summary['ride_id']} with avg {summary['avg_power']}W and TSS {summary.get('tss', 0)}\n")
        except Exception as e:
            print(f"❌ Failed to process {filename}: {e}\n")
        time.sleep(1)  # Add slight delay to avoid API rate limits


if __name__ == "__main__":
    backfill_all_rides()
