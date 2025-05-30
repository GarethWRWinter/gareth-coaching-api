# api/routes.py

from fastapi import APIRouter, HTTPException
from scripts.ride_processor import process_latest_fit_file, get_all_rides, get_ride
from scripts.dropbox_auth import refresh_dropbox_token

router = APIRouter()

@router.get("/latest-ride-data")
def latest_ride_data():
    try:
        access_token = refresh_dropbox_token()
        ride_data, ride_summary = process_latest_fit_file(access_token=access_token)
        return ride_summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process latest ride: {str(e)}")

@router.get("/ride-history")
def ride_history():
    try:
        rides = get_all_rides()
        return rides
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch ride history: {str(e)}")
