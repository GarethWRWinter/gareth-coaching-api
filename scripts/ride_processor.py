import os
import dropbox
import tempfile
from scripts.dropbox_auth import refresh_dropbox_token
from scripts.dropbox_utils import get_latest_fit_file_metadata, download_file
from scripts.fit_parser import parse_fit_file
from scripts.sanitize import sanitize_fit_data
from scripts.fit_metrics import calculate_ride_metrics
from scripts.database import save_ride_summary


def process_latest_fit_file(access_token: str) -> dict:
    # Refresh token if needed
    dbx = dropbox.Dropbox(oauth2_access_token=access_token)

    # Get latest .FIT file metadata
    metadata = get_latest_fit_file_metadata(dbx)
    if not metadata:
        raise FileNotFoundError("No FIT files found in Dropbox folder.")

    # Download latest .FIT file to temp path
    with tempfile.NamedTemporaryFile(suffix=".fit", delete=False) as tmp_file:
        download_file(dbx, metadata.path_lower, tmp_file.name)
        fit_path = tmp_file.name

    # Parse raw data
    raw_data = parse_fit_file(fit_path)

    # Sanitize for processing
    sanitized = sanitize_fit_data(raw_data)

    # Compute metrics
    summary = calculate_ride_metrics(sanitized)

    # Attach ride ID and store in DB
    ride_id = save_ride_summary(summary)

    # Cleanup temp file
    os.remove(fit_path)

    return {
        "ride_id": ride_id,
        "summary": summary
    }
