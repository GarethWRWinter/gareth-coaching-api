from fastapi import APIRouter, HTTPException
from scripts.save_latest_ride_to_db import process_latest_fit_file
from scripts.ride_database import fetch_ride_history
from scripts.refresh_token_handler import get_dropbox_access_token
from scripts.sanitize import sanitize

router = APIRouter()


@router.get("/latest-ride-data")
def get_latest_ride_data():
    try:
        access_token = get_dropbox_access_token()
        result = process_latest_fit_file(access_token)
        return sanitize(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rides")
def get_all_rides():
    try:
        ride_history = fetch_ride_history()
        return sanitize(ride_history)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
