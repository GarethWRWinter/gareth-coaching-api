from fastapi import APIRouter, HTTPException
from scripts.save_latest_ride_to_db import process_latest_fit_file
from scripts.ride_database import get_all_rides, get_ride_by_id
from scripts.dropbox_auth import refresh_dropbox_token

router = APIRouter()

@router.get("/ride-history")
def ride_history():
    rides = get_all_rides()
    return rides

@router.get("/ride/{ride_id}")
def get_ride(ride_id: str):
    if ride_id == "latest":
        result = process_latest_fit_file()
        if result is None:
            raise HTTPException(status_code=404, detail="404: No rides found.")
        return result
    else:
        ride = get_ride_by_id(ride_id)
        if not ride:
            raise HTTPException(status_code=404, detail="404: Ride not found.")
        return ride
