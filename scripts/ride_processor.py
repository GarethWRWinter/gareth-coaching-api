import logging
from scripts.fetch_and_parse import process_latest_fit_file
from scripts.ride_database import store_ride

logger = logging.getLogger(__name__)

def process_and_store_latest_fit_file():
    try:
        ride_id, summary, seconds = process_latest_fit_file()
        store_ride(ride_id, summary, seconds)
        return summary
    except Exception as e:
        logger.exception("Failed to process latest ride")
        raise
