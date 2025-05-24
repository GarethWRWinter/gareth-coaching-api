import os
from dotenv import load_dotenv
from scripts.dropbox_auth import refresh_dropbox_token
from scripts.dropbox_utils import list_fit_files, download_file_from_dropbox
from scripts.ride_database import store_ride, ride_exists
from scripts.ride_processor import process_fit_file

load_dotenv()

DROPBOX_FOLDER = os.getenv("DROPBOX_FOLDER", "/Apps/WahooFitness")
DROPBOX_TOKEN = os.getenv("DROPBOX_TOKEN")

def backfill_all_fit_files():
    print(f"🔄 Starting backfill from Dropbox folder: {DROPBOX_FOLDER}")

    access_token = refresh_dropbox_token()
    filenames = list_fit_files(DROPBOX_FOLDER, access_token)

    print(f"📁 Found {len(filenames)} .fit files in Dropbox.")

    for filename in filenames:
        print(f"📂 Processing: {filename}")

        # Use filename to generate ride_id
        ride_id = filename.replace(".fit", "").replace("/", "_")

        if ride_exists(ride_id):
            print(f"⏩ Ride {ride_id} already exists in DB. Skipping.")
            continue

        try:
            local_path = f"/tmp/{filename.split('/')[-1]}"
            download_file_from_dropbox(filename, local_path, access_token)

            summary, second_by_second = process_fit_file(local_path)

            store_ride(summary, second_by_second)
            print(f"✅ Stored ride {ride_id} to database.")

        except Exception as e:
            print(f"❌ Failed to process {filename}: {e}")

if __name__ == "__main__":
    backfill_all_fit_files()
