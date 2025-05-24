# scripts/save_latest_ride_to_db.py

from scripts.ride_database import store_ride
from scripts.ride_processor import process_latest_fit_file

def save_ride_to_db():
    """
    Processes the latest FIT file and stores it in the database.
    """
    full_data, summary = process_latest_fit_file()
    store_ride(summary, full_data)
    return {"status": "success", "ride_id": summary.get("ride_id")}
