# scripts/ride_processor.py

import os
from scripts.fetch_fit_from_dropbox import get_latest_fit_file_from_dropbox
from scripts.fit_parser import parse_fit_file
from scripts.fit_metrics import calculate_ride_metrics
from scripts.ride_database import store_ride
from scripts.sanitize import sanitize

def process_latest_fit_file():
    """
    Downloads, parses, analyzes, and stores the latest FIT file from Dropbox.
    Returns sanitized summary and second-by-second data.
    """
    # Get FTP from environment variable
    ftp = int(os.getenv("FTP", 250))  # Default fallback

    # Download and parse latest ride
    fit_path, file_name = get_latest_fit_file_from_dropbox()
    fit_df, metadata = parse_fit_file(fit_path)

    # Calculate metrics using FTP
    summary, seconds = calculate_ride_metrics(fit_df, metadata, ftp)

    # Store in database
    store_ride(summary, seconds)

    # Return sanitized response
    return sanitize(summary), sanitize(seconds)
