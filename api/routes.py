from fastapi import APIRouter
from fastapi.responses import JSONResponse
from scripts.ride_processor import (
    process_latest_fit_file,
    get_all_ride_summaries,
    get_ride_by_id,
    backfill_all_rides
)

router = APIRouter()

@router.get("/latest-ride-data")
def latest_ride_data():
    try:
        ride_summary, ride_data = process_latest_fit_file()
        return {
            "summary": ride_summary,
            "data": ride_data
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": f"Failed to process latest ride: {e}"})

@router.get("/ride-history")
def ride_history():
    try:
        return get_all_ride_summaries()
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": f"Failed to fetch ride history: {e}"})

@router.get("/ride/{ride_id}")
def get_ride(ride_id: str):
    try:
        return get_ride_by_id(ride_id)
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": f"Failed to fetch ride {ride_id}: {e}"})

@router.post("/backfill")
def backfill_rides():
    try:
        return backfill_all_rides()
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": f"Backfill failed: {e}"})
