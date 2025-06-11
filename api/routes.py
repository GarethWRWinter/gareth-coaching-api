# api/routes.py

from fastapi import APIRouter, HTTPException
from scripts.ride_processor import (
    process_latest_ride,
    get_ride_history
)

router = APIRouter()

@router.get("/latest-ride-data")
async def latest_ride_data():
    try:
        # Replace with the actual path to your FIT file and correct FTP value
        path_to_fit = "/mnt/data/latest.fit"
        ftp = 250  # <-- Set the rider's actual FTP here
        result = process_latest_ride(path_to_fit, ftp)
        return result
    except Exception as err:
        raise HTTPException(status_code=500, detail=f"Failed to process latest ride: {err}")

@router.get("/ride-history")
async def ride_history():
    try:
        rides = get_ride_history()  # no arguments expected
        return rides
    except Exception as err:
        raise HTTPException(status_code=500, detail=f"Failed to fetch ride history: {err}")
