from fastapi import APIRouter, HTTPException
from scripts.save_latest_ride_to_db import process_latest_fit_file
from scripts.dropbox_auth import refresh_dropbox_token
from scripts.ride_database import get_all_rides, get_ride_by_id

router = APIRouter()

@router.get("/latest-ride-data")
def get_latest_ride_data():
    """Fetch, parse, save and return full data for the latest ride from Dropbox"""
    access_token = refresh_dropbox_token()
    result = process_latest_fit_file(access_token)
    if result is None:
        raise HTTPException(status_code=404, detail="No FIT file found or failed to process.")
    return result

@router.get("/ride-history")
def ride_history():
    """Get all rides stored in the database"""
    return get_all_rides()

@router.get("/ride/{ride_id}")
def ride_by_id(ride_id: str):
    """Fetch ride data by ride ID or the keyword 'latest'"""
    if ride_id == "latest":
        rides = get_all_rides()
        if not rides:
            raise HTTPException(status_code=404, detail="404: No rides found.")
        ride_id = rides[-1]["id"]
    ride = get_ride_by_id(ride_id)
    if ride is None:
        raise HTTPException(status_code=404, detail="404: Ride not found.")
    return ride
