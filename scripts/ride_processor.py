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
    
    summary, full_data = calculate_ride_# scripts/ride_processor.py

from scripts.dropbox_utils import list_fit_files, download_file_from_dropbox
from scripts.parse_fit import parse_fit_file
from scripts.fit_metrics import calculate_ride_metrics
from scripts.sanitize import sanitize
from scripts.ride_database import store_ride

def process_latest_fit_file(access_token: str):
    # List available .fit files
    fit_files = list_fit_files(access_token)
    if not fit_files:
        raise ValueError("No .fit files found in Dropbox folder.")

    latest_file = sorted(fit_files, key=lambda x: x["client_modified"], reverse=True)[0]
    file_path = latest_file["path_display"]

    # Download latest .fit file
    file_content = download_file_from_dropbox(file_path, access_token)

    # Parse FIT file into raw DataFrame
    raw_df = parse_fit_file(file_content)

    # Calculate metrics
    summary = calculate_ride_metrics(raw_df)

    # Sanitize outputs for storage and JSON response
    sanitized_summary = sanitize(summary)
    sanitized_data = sanitize(raw_df.to_dict(orient="records"))

    # Store in DB
    store_ride(summary=sanitized_summary, full_data=sanitized_data)

    return sanitized_data, sanitized_summary
metrics(full_data, summary)
    return sanitize(full_data), sanitize(summary)
