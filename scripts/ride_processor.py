# scripts/ride_processor.py

from scripts.fetch_fit_from_dropbox import get_latest_fit_file_from_dropbox
from scripts.fit_metrics import calculate_ride_metrics
from scripts.sanitize import sanitize

def process_latest_fit_file():
    """
    Fetch, parse, and analyze the latest FIT file from Dropbox.
    Returns sanitized full_data and summary dictionaries.
    """
    full_data, summary = get_latest_fit_file_from_dropbox()
    if not full_data or not summary:
        raise ValueError("Failed to process latest ride file")
    
    summary, full_data = calculate_ride_metrics(full_data, summary)
    return sanitize(full_data), sanitize(summary)
