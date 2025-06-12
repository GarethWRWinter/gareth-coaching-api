from fastapi import APIRouter, HTTPException, Query
from scripts.ride_processor import process_latest_fit_file, get_all_rides

router = APIRouter()

@router.get("/latest-ride-data")
def latest_ride_data(ftp: float = Query(..., description="Functional Threshold Power")):
    try:
        return process_latest_fit_file("/mnt/data/latest.fit", ftp)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process latest ride: {e}")

@router.get("/ride-history")
def ride_history():
    try:
        rides = get_all_rides()
        return rides
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch ride history: {e}")
