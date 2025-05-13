from fastapi import APIRouter
from fastapi.responses import JSONResponse
from scripts.refresh_token import get_dropbox_access_token
from scripts.save_latest_ride_to_db import process_latest_fit_file
from scripts.ride_database import fetch_ride_history

router = APIRouter()

@router.get("/latest-ride-data")
def get_latest_ride_data():
    access_token = get_dropbox_access_token()
    result = process_latest_fit_file(access_token)
    return JSONResponse(content=result)

@router.get("/ride-history")
def get_ride_history():
    rides = fetch_ride_history()
    return JSONResponse(content=rides)
