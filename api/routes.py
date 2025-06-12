from fastapi import APIRouter, HTTPException, Query
from scripts.ride_processor import process_latest_fit_file, get_all_rides
import os

router = APIRouter()

@router.get("/latest-ride-data")
def latest_ride_data(ftp: int = Query(default=None)):
    try:
        ftp = ftp or int(os.getenv("FTP", "308"))
        data = process_latest_fit_file(ftp=ftp)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process latest ride: {str(e)}")

@router.get("/ride-history")
def ride_history():
    try:
        return {"rides": get_all_rides()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch ride history: {str(e)}")
