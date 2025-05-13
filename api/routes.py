from fastapi import APIRouter
from fastapi.responses import JSONResponse
from scripts.save_latest_ride_to_db import process_latest_fit_file
from scripts.dropbox_auth import refresh_access_token  # ✅ FIXED: Correct import
from scripts.ride_database import fetch_ride_history
from scripts.time_in_zones import calculate_time_in_zones  # used in summary response
from scripts.sanitize import sanitize

router = APIRouter()

@router.get("/latest-ride-data")
def get_latest_ride_data():
    access_token = refresh_access_token()
    result = process_latest_fit_file(access_token)
    return JSONResponse(content=sanitize(result))

@router.get("/rides")
def get_all_rides():
    rides = fetch_ride_history()
    return JSONResponse(content=sanitize(rides))
