import os
from scripts.fetch_fit_from_dropbox import get_latest_fit_file_from_dropbox
from scripts.fit_parser import parse_fit, calculate_ride_metrics
from scripts.sanitize import sanitize

def process_latest_fit_file(access_token: str):
    try:
        file_path, file_name = get_latest_fit_file_from_dropbox(access_token)

        df = parse_fit(file_path)
        summary = calculate_ride_metrics(df, ftp=308)  # use your current FTP

        return df, summary

    except Exception as e:
        raise RuntimeError(f"Failed to process latest ride: {e}")

# For long-term use — used by /ride-history and backfill scripts
def get_all_ride_summaries(db_session=None):
    from scripts.ride_database import fetch_all_ride_summaries
    return fetch_all_ride_summaries()

def get_ride_by_id(ride_id: str, db_session=None):
    from scripts.ride_database import fetch_ride_by_id
    return fetch_ride_by_id(ride_id)

def backfill_all_rides():
    from scripts.backfill_from_dropbox import backfill_historical_rides
    return backfill_historical_rides()
