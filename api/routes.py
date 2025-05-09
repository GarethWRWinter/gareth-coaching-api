from fastapi import APIRouter
from dropbox_auth import get_dropbox_access_token
from scripts.save_latest_ride_to_db import save_latest_ride_to_db

router = APIRouter()

@router.get("/latest-ride-data")
def get_latest_ride_data():
    access_token = get_dropbox_access_token()
    result = save_latest_ride_to_db(access_token)
    return result
