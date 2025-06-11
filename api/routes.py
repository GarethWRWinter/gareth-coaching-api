from fastapi import APIRouter, HTTPException
from scripts.ride_processor import (
    process_latest_fit_file,
    get_all_rides,
    get_trend_analysis,
    get_power_trends,
    detect_and_update_ftp
)
from scripts.fetch_fit_from_dropbox import get_latest_fit_file_from_dropbox
from scripts.dropbox_auth import refresh_dropbox_token
import os

router = APIRouter()

@router.get("/latest-ride-data")
def latest_ride_data():
    try:
        ftp = 308.0  # Replace with dynamic FTP logic later if needed

        # Refresh the Dropbox access token
        new_access_token = refresh_dropbox_token()

        # Get Dropbox folder path
        folder_path = os.environ.get("DROPBOX_FOLDER", "/Apps/WahooFitness")

        # Download the latest .fit file using the refreshed token
        local_path = get_latest_fit_file_from_dropbox(new_access_token, folder_path)

        # Process the latest .fit file
        return process_latest_fit_file(local_path, ftp)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process latest ride: {str(e)}")

@router.get("/ride-history")
def ride_history():
    return get_all_rides()

@router.get("/trend-analysis")
def trend_analysis():
    return get_trend_analysis()

@router.get("/power-trends")
def power_trends():
    return get_power_trends()

@router.get("/ftp-update")
def ftp_update():
    return detect_and_update_ftp()
