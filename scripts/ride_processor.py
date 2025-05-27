import os
import logging
from datetime import datetime
from scripts.parse_fit import parse_fit_file
from scripts.fit_metrics import calculate_ride_metrics
from scripts.ride_database import store_ride

def process_fit_file(file_path: str) -> bool:
    """
    Parse a .fit file, compute metrics, and store it in the database.
    Returns True if stored successfully.
    """
    try:
        # Parse the file
        data = parse_fit_file(file_path)
        if not data:
            logging.warning(f"No data parsed from: {file_path}")
            return False

        # Compute metrics
        summary = calculate_ride_metrics(data)
        if not summary:
            logging.warning(f"Metrics could not be calculated for: {file_path}")
            return False

        # Build ride ID from filename
        ride_id = os.path.basename(file_path).replace(".fit", "").replace("/", "_")

        # Store ride
        store_ride(ride_id, summary)
        logging.info(f"Stored ride {ride_id} successfully.")
        return True

    except Exception as e:
        logging.error(f"Failed to process file {file_path}: {str(e)}")
        return False
