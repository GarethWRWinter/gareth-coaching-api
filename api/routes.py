from fastapi import APIRouter
from fastapi.responses import JSONResponse
from scripts.dropbox_auth import refresh_dropbox_token
from scripts.ride_processor import process_latest_fit_file
from scripts.ride_database import get_ride_by_id, get_all_rides

router = APIRouter()

@router.get("/ride-history")
def get_ride_history():
    return get_all_rides()

@router.get("/ride/{ride_id}")
def get_ride(ride_id: str):
    if ride_id == "latest":
        access_token = refresh_dropbox_token()
        result = process_latest_fit_file(access_token)
        if "error" in result:
            return JSONResponse(content=result, status_code=500)
        return result
    else:
        ride = get_ride_by_id(ride_id)
        if ride:
            return ride
        return JSONResponse(content={"error": "Ride not found"}, status_code=404)

@router.get("/latest-ride-data")
def get_latest_ride_data():
    access_token = refresh_dropbox_token()
    result = process_latest_fit_file(access_token)
    if "error" in result:
        return JSONResponse(content=result, status_code=500)
    return result
