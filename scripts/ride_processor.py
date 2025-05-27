import os
import logging
from scripts.parse_fit import parse_fit_file
from scripts.fit_metrics import calculate_ride_metrics
from scripts.ride_database import store_ride

def process_fit_file(file_path: str) -> bool:
    """
    Parses a .fit file, calculates ride metrics, and stores the result.
    Returns True if successful, False otherwise.
    """
    try:
        data = parse_fit_file(file_path)
        if not data or data.empty:
            logging.warning(f"Empty or invalid data from {file_path}")
            return False

        summary = calculate_ride_metrics(data)
        if not summary:
            logging.warning(f"Metrics not computed for {file_path}")
            return False

        ride_id = summary.get("ride_id") or os.path.basename(file_path).replace(".fit", "")
        store_ride(ride_id, summary)
        logging.info(f"Ride {ride_id} processed and stored successfully.")
        return True

    except Exception as e:
        logging.error(f"Error processing {file_path}: {e}")
        return False
