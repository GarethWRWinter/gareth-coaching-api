# api/routes.py

from fastapi import APIRouter, HTTPException
from scripts.ride_processor import process_latest_fit_file, get_all_rides

router = APIRouter()

@router.get("/latest-ride-data")
def latest_ride_data():
    try:
        filepath = "path/to/latest_data.csv"  # update per your ingestion method
        return process_latest_fit_file(filepath)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ride-history")
def ride_history():
    return get_all_rides()
