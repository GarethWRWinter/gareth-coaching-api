from scripts.ride_database import store_ride
import logging

logger = logging.getLogger(__name__)

def save_ride_to_db(summary, full_data):
    try:
        store_ride(summary, full_data)
        logger.info(f"Saved ride {summary['ride_id']} to database.")
    except Exception as e:
        logger.exception("Failed to save latest ride to DB")
        raise
