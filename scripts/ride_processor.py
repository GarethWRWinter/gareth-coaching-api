# scripts/ride_processor.py

from scripts.fetch_fit_from_dropbox import process_fit_file
from scripts.save_latest_ride_to_db import save_ride_to_db

def process_and_store_ride(file_path):
    try:
        fit_data, ride_summary = process_fit_file(file_path)
        ride_id = ride_summary.get("ride_id")
        if ride_id:
            save_ride_to_db(ride_id, ride_summary)
            print(f"[✅] Ride {ride_id} saved successfully.")
        else:
            print("[⚠️] No ride_id found in summary.")
        return ride_summary
    except Exception as e:
        print(f"[❌] Failed to process and store ride: {e}")
        return None
