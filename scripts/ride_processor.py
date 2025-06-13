import os
from scripts.dropbox_utils import list_fit_files, download_fit_file
from scripts.parse_fit import parse_fit_file
from scripts.fit_metrics import calculate_ride_metrics
from scripts.ride_database import store_ride, get_ride_history, get_ride_by_id
from scripts.sanitize import sanitize


def process_latest_fit_file():
    """Fetch, parse, analyze and store the latest .fit file."""
    try:
        fit_files = list_fit_files()
        if not fit_files:
            return {"error": "No .fit files found in Dropbox"}

        latest_file = sorted(fit_files)[-1]
        local_path = download_fit_file(latest_file)

        fit_df = parse_fit_file(local_path)
        ride_summary = calculate_ride_metrics(fit_df, latest_file)
        store_ride(ride_summary, fit_df)

        return sanitize({"summary": ride_summary, "data": fit_df.to_dict(orient="records")})
    except Exception as e:
        return {"error": f"Failed to process latest ride: {str(e)}"}
