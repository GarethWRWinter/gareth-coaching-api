from fastapi import APIRouter
from dropbox_auth import refresh_dropbox_token
from scripts.save_latest_ride_to_db import save_latest_ride_to_db

router = APIRouter()

@router.get("/latest-ride-data")
def get_latest_ride_data():
    access_token = refresh_dropbox_token()
    result = save_latest_ride_to_db(access_token)
    return result

@router.get("/")
def root():
    return {"status": "OK", "message": "Gareth Coaching API is live"}
