import logging
from scripts.dropbox_fetch import get_latest_fit_file_from_dropbox
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
    file_bytes, filename, timestamp_str = get_latest_fit_file_from_dropbox()
    fit_data = parse_fit_file(file_bytes)
    ride_summary = calculate_ride_metrics(fit_data, timestamp_str)
    store_ride(ride_summary, fit_data)
    return ride_summary, fit_data
