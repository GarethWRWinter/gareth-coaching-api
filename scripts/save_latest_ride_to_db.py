# scripts/save_latest_ride_to_db.py

import logging
from scripts.ride_database import store_ride
from scripts.sanitize import sanitize

logger = logging.getLogger(__name__)

def save_ride_to_db(summary: dict):
    try:
        cleaned = sanitize(summary)
        store_ride(cleaned)
        logger.info(f"Saved ride {cleaned.get('ride_id')} to database.")
    except Exception as e:
        logger.error("Failed to save ride to DB", exc_info=True)
        raise
