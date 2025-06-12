# api/routes.py
from fastapi import APIRouter, HTTPException, Query
from scripts.ride_processor import process_latest_fit_file, get_all_rides

router = APIRouter()

@router.get("/latest-ride-data")
async def latest_ride_data(ftp: float = Query(..., gt=0, description="Functional Threshold Power")):
    try:
        data = process_latest_fit_file(ftp)
        return data
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process latest ride: {e}")

@router.get("/ride-history")
async def ride_history():
    try:
        history = get_all_rides()
        return {"rides": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch ride history: {e}")
