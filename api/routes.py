from fastapi import APIRouter, HTTPException
from scripts.refresh_token import get_dropbox_access_token
from scripts.save_latest_ride_to_db import process_latest_fit_file

router = APIRouter()

@router.get("/latest-ride-data")
def get_latest_ride_data():
    try:
        access_token = get_dropbox_access_token()
        result = process_latest_fit_file(access_token)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
