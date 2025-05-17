import os
from scripts.dropbox_utils import get_latest_fit_file_path, download_file
from scripts.parse_fit_to_df import parse_fit_file_to_dataframe
from scripts.sanitize import sanitize_fit_data
from scripts.fit_metrics import calculate_ride_metrics
from scripts.ride_database import save_ride_summary


def process_latest_fit_file(access_token: str) -> dict:
    """
    Downloads the latest .FIT file from Dropbox, parses it into a sanitized DataFrame,
    computes ride metrics, and stores the summary in the SQLite database.
    Returns the ride summary dictionary.
    """
    # Step 1: Get latest file path
    latest_file_path = get_latest_fit_file_path(access_token)
    if not latest_file_path:
        raise FileNotFoundError("No .FIT files found in Dropbox.")

    # Step 2: Download the file locally
    local_file_path = "latest.fit"
    download_file(access_token, latest_file_path, local_file_path)

    # Step 3: Parse and sanitize FIT file
    raw_df = parse_fit_file_to_dataframe(local_file_path)
    sanitized_df = sanitize_fit_data(raw_df)

    # Step 4: Compute ride metrics
    summary = calculate_ride_metrics(sanitized_df)

    # ✅ Safety check for required keys before DB write
    required_keys = ["ride_id", "start_time", "duration", "distance_km", "avg_power", "avg_heart_rate"]
    for key in required_keys:
        if key not in summary:
            raise KeyError(f"Missing required field in summary: {key}")

    # Step 5: Save summary to database
    save_ride_summary(summary)

    return summary
