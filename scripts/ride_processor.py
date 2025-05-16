import os
import pandas as pd
from scripts.dropbox_fetcher import fetch_latest_fit_file
from scripts.parse_fit_to_df import parse_fitfile_to_dataframe
from scripts.sanitize import sanitize_fit_data
from scripts.ride_database import store_ride_data
from scripts.dropbox_auth import refresh_dropbox_token


def process_latest_fit_file(access_token: str) -> dict:
    print("🔄 Refreshing Dropbox token...")
    access_token = refresh_dropbox_token()

    print("📥 Fetching latest FIT file from Dropbox...")
    local_fit_path = fetch_latest_fit_file(access_token)

    print("📊 Parsing FIT file to DataFrame...")
    df = parse_fitfile_to_dataframe(local_fit_path)

    print("🧹 Sanitizing DataFrame...")
    sanitized_df = sanitize_fit_data(df)

    print("💾 Storing ride data in database...")
    ride_metadata = store_ride_data(sanitized_df)

    return {
        "message": "✅ Ride processed and stored successfully.",
        "ride_metadata": ride_metadata,
    }
