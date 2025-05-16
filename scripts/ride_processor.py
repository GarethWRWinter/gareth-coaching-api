import os
from scripts.dropbox_utils import get_latest_fit_file_metadata, download_file
from scripts.parse_fit_to_df import parse_fit_file_to_dataframe
from scripts.sanitize import sanitize_fit_data
from scripts.fit_metrics import calculate_ride_metrics
from scripts.ride_database import save_ride_summary

def process_latest_fit_file(access_token: str):
    # Step 1: Get metadata of latest .FIT file
    metadata = get_latest_fit_file_metadata(access_token)
    if "error" in metadata:
        raise RuntimeError(f"Dropbox error: {metadata['error']}")

    dropbox_path = metadata["path_display"]
    filename = os.path.basename(dropbox_path)
    local_path = f"/tmp/{filename}"

    # Step 2: Download file from Dropbox
    download_result = download_file(access_token, dropbox_path, local_path)
    if not download_result:
        raise RuntimeError("Failed to download file from Dropbox.")

    # Step 3: Parse FIT to DataFrame
    df = parse_fit_file_to_dataframe(local_path)
    if df is None or df.empty:
        raise ValueError("Parsed DataFrame is empty or invalid.")

    # Step 4: Sanitize + calculate metrics
    sanitized = sanitize_fit_data(df)
    summary = calculate_ride_metrics(sanitized)

    # Step 5: Store to database
    save_ride_summary(summary)

    return summary
