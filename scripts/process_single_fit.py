import os
import logging
from scripts.ride_database import store_ride
from scripts.fit_metrics import calculate_ride_metrics
from scripts.parse_fit import parse_fit_file
from scripts.sanitize import sanitize

def process_fit_file(fit_file_path):
    try:
        fit_data = parse_fit_file(fit_file_path)
        if not fit_data or len(fit_data) < 2:
            logging.warning(f"No valid data found in {fit_file_path}")
            return None, None

        ride_summary = calculate_ride_metrics(fit_data)
        ride_id = ride_summary.get("ride_id") or os.path.basename(fit_file_path).replace(".fit", "")
        ride_summary["ride_id"] = ride_id

        sanitized_summary = sanitize(ride_summary)
        sanitized_fit_data = sanitize(fit_data)
        store_ride(sanitized_summary, sanitized_fit_data)

        return sanitized_summary, sanitized_fit_data
    except Exception as e:
        logging.error(f"Error processing {fit_file_path}: {e}")
        return None, None
