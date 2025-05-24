# scripts/ride_processor.py

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

    # Get the most recent file
    latest_file = sorted(fit_files, key=lambda x: x["client_modified"], reverse=True)[0]
    file_path = latest_file["path_display"]

    # Download the .fit file
    file_content = download_file_from_dropbox(file_path, access_token)

    # Parse the raw data
    raw_df = parse_fit_file(file_content)

    # Compute ride summary metrics
    summary = calculate_ride_metrics(raw_df)

    # Sanitize before storage and response
    sanitized_summary = sanitize(summary)
    sanitized_data = sanitize(raw_df.to_dict(orient="records"))

    # Store in the database
    store_ride(sanitized_summary, sanitized_data)

    return sanitized_data, sanitized_summary
