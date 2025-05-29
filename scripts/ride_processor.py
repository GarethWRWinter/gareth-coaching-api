from scripts.dropbox_auth import refresh_dropbox_token
from scripts.fetch_fit_from_dropbox import get_latest_fit_file_from_dropbox
from scripts.fit_parser import calculate_ride_metrics
from scripts.sanitize import sanitize

def process_latest_fit_file():
    try:
        access_token = refresh_dropbox_token()
        file_path, file_name = get_latest_fit_file_from_dropbox(access_token)
        ride_summary, ride_data = calculate_ride_metrics(file_path, file_name)
        return sanitize(ride_summary), sanitize(ride_data)
    except Exception as e:
        raise RuntimeError(f"Failed to process latest ride: {e}")

# These will be implemented later
def get_all_ride_summaries():
    raise NotImplementedError("This function will return a history of all rides.")

def get_ride_by_id(ride_id):
    raise NotImplementedError("This function will return a specific ride by ID.")

def backfill_all_rides():
    raise NotImplementedError("This function will load historical rides from Dropbox.")
