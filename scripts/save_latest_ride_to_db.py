import logging
from scripts.ride_processor import process_latest_fit_file
from scripts.ride_database import store_ride

logger = logging.getLogger(__name__)

def save_latest_ride_to_db():
    """
    Processes the latest .fit file from Dropbox and stores the ride in the database.
    Returns:
        Tuple (full_data: list, summary: dict)
    """
    try:
        full_data, summary = process_latest_fit_file()
        store_ride(summary, full_data)
        return full_data, summary
    except Exception as e:
        logger.error(f"Failed to process and save latest ride: {e}")
        raise RuntimeError(f"Failed to process latest ride: {e}")
