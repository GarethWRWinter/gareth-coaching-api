from fastapi import APIRouter, HTTPException
from scripts.dropbox_auth import refresh_dropbox_token
from scripts.ride_processor import process_latest_fit_file
from scripts.ride_database import get_all_rides, get_ride_by_id

router = APIRouter()

@router.get("/ride-history")
def ride_history():
    rides = get_all_rides()
    return {"rides": rides}

@router.get("/ride/latest")
def get_ride():
    access_token = refresh_dropbox_token()
    result = process_latest_fit_file(access_token)
    return result

@router.get("/ride/{ride_id}")
def get_ride_by_id_route(ride_id: str):
    if ride_id == "latest":
        access_token = refresh_dropbox_token()
        result = process_latest_fit_file(access_token)
        return result
    ride = get_ride_by_id(ride_id)
    if ride:
        return ride
    raise HTTPException(status_code=404, detail="Ride not found")
