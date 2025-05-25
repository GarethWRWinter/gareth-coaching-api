from scripts.ride_database import store_ride
from scripts.fetch_and_parse import process_latest_fit_file
import logging

logger = logging.getLogger(__name__)

def save_ride_to_db():
    try:
        ride_summary = process_latest_fit_file()  # ✅ No arguments needed
        store_ride(ride_summary)
        logger.info(f"Saved ride {ride_summary['ride_id']} to database.")
    except Exception as e:
        logger.exception("Failed to save latest ride to DB")
        raise
