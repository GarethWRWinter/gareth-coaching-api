import os
from scripts.dropbox_utils import list_fit_files_in_folder, download_file
from scripts.ride_database import ride_exists, save_ride_summary
from scripts.ride_processor import process_fit_file
from scripts.dropbox_auth import refresh_dropbox_token


def backfill_all_dropbox_rides():
    print("🔁 Starting Dropbox backfill...")

    # Step 1: Get a fresh Dropbox access token
    access_token = refresh_dropbox_token()

    # Step 2: List all .fit files in the configured Dropbox folder
    fit_files = list_fit_files_in_folder(access_token)
    print(f"📂 Found {len(fit_files)} .FIT files in Dropbox")

    processed = 0
    skipped = 0
    failed = 0

    for file_metadata in fit_files:
        dropbox_path = file_metadata["path_display"]

        # Check if ride already exists in DB using filename timestamp
        ride_id = os.path.splitext(os.path.basename(dropbox_path))[0]
        if ride_exists(ride_id):
            print(f"⏭️  Skipping existing ride: {ride_id}")
            skipped += 1
            continue

        try:
            # Step 3: Download file
            local_path = f"temp_{ride_id}.fit"
            download_file(access_token, dropbox_path, local_path)

            # Step 4: Process ride and save
            summary = process_fit_file(local_path)
            save_ride_summary(summary)
            print(f"✅ Processed and saved: {ride_id}")
            processed += 1

            # Clean up temp file
            os.remove(local_path)

        except Exception as e:
            print(f"❌ Failed to process {dropbox_path}: {e}")
            failed += 1

    print("🎯 Dropbox backfill complete.")
    print(f"✅ Processed: {processed}, ⏭️ Skipped: {skipped}, ❌ Failed: {failed}")


if __name__ == "__main__":
    backfill_all_dropbox_rides()
