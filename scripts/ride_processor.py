import logging
from scripts.fetch_and_parse import process_latest_fit_file
from scripts.ride_database import store_ride

logger = logging.getLogger(__name__)

def process_and_store_latest_fit_file():
    try:
        summary = process_latest_fit_file()
        store_ride(summary)
        return summary
    except Exception as e:
        logger.exception("Failed to process latest ride")
        raise
