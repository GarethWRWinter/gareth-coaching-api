import os
from scripts.ride_processor import process_fit_file
from scripts.ride_database import ride_exists, save_ride_summary

LOCAL_FIT_FOLDER = "fit_files_local"
DEFAULT_FTP = 308  # Set your current FTP here

def backfill_local_fit_files():
    fit_files = [
        f for f in os.listdir(LOCAL_FIT_FOLDER)
        if f.lower().endswith(".fit")
    ]

    print(f"Found {len(fit_files)} .fit files in {LOCAL_FIT_FOLDER}")

    for filename in fit_files:
        ride_id = filename.replace(".fit", "")
        if ride_exists(ride_id):
            print(f"❌ Skipping {filename} (already exists in DB)")
            continue

        filepath = os.path.join(LOCAL_FIT_FOLDER, filename)
        try:
            print(f"✅ Processing {filename}...")
            summary = process_fit_file(filepath, DEFAULT_FTP)
            save_ride_summary(summary)
            print(f"✅ Saved {ride_id}")
        except Exception as e:
            print(f"❌ Error processing {filename}: {e}")

if __name__ == "__main__":
    backfill_local_fit_files()
