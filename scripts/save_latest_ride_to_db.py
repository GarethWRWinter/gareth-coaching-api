from scripts.ride_database import store_ride
from scripts.fetch_and_parse import process_latest_fit_file
import os
import logging

logger = logging.getLogger(__name__)

def save_ride_to_db():
    try:
        access_token = os.getenv("DROPBOX_TOKEN")
        if not access_token:
            raise ValueError("Missing Dropbox access token.")

        summary, full_data = process_latest_fit_file(access_token)
        store_ride(summary, full_data)
        logger.info(f"Saved ride {summary['ride_id']} to database.")

    except Exception as e:
        logger.exception("Failed to save latest ride to DB")
        raise
