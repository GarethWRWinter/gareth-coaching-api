from scripts.ride_database import store_ride
from scripts.ride_processor import process_latest_fit_file
from scripts.dropbox_auth import refresh_dropbox_token


def save_latest_ride_to_db():
    access_token = refresh_dropbox_token()
    summary, full_data = process_latest_fit_file(access_token)
    store_ride(summary, full_data)
    return summary
