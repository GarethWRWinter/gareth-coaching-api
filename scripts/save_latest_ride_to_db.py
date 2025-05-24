import logging
from scripts.ride_database import store_ride

logger = logging.getLogger(__name__)

def save_ride_to_db(summary: dict):
    try:
        store_ride(summary)
        logger.info(f"Saved ride {summary['ride_id']} to database.")
    except Exception as e:
        logger.exception("Failed to save latest ride to DB")
        raise
