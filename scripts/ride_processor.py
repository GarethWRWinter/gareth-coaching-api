import logging
from scripts.fetch_fit_from_dropbox import get_latest_fit_file_from_dropbox
from scripts.fit_parser import parse_fit_file
from scripts.fit_metrics import calculate_ride_metrics
from scripts.ride_database import store_ride

logger = logging.getLogger(__name__)

def process_latest_fit_file():
    """
    Fetch, parse, calculate, and store the latest ride from Dropbox.
    Returns:
        tuple: (ride_summary: dict, full_fit_data: list of dicts)
    """
    # Step 1: Get latest .fit file from Dropbox
    file_bytes, filename, timestamp_str = get_latest_fit_file_from_dropbox()

    # Step 2: Parse the FIT file into a clean list of data points
    fit_data = parse_fit_file(file_bytes)

    # Step 3: Calculate ride summary metrics
    ride_summary = calculate_ride_metrics(fit_data, timestamp_str)

    # Step 4: Store summary + full FIT in SQLite
    store_ride(ride_summary, fit_data)

    return ride_summary, fit_data
