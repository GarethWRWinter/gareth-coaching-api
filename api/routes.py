from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from scripts.fetch_and_parse import process_latest_fit_file
from scripts.save_latest_ride_to_db import save_ride_to_db
from scripts.sanitize import sanitize
from scripts.ride_database import get_all_rides, get_ride_by_id
from scripts.trend_analysis import compute_trend_metrics

router = APIRouter()

@router.get("/latest-ride-data")
async def get_latest_ride_data():
    try:
        summary, full_data = process_latest_fit_file()
        save_ride_to_db(summary, full_data)
        return JSONResponse(content=sanitize(summary))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process latest ride: {str(e)}")

@router.get("/ride-history")
def ride_history():
    try:
        rides = get_all_rides()
        return sanitize(rides)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not fetch ride history: {str(e)}")

@router.get("/ride/{ride_id}")
def get_ride(ride_id: str):
    try:
        ride = get_ride_by_id(ride_id)
        if ride is None:
            raise HTTPException(status_code=404, detail="Ride not found")
        return sanitize(ride)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching ride {ride_id}: {str(e)}")

@router.get("/trend-analysis")
def get_trend_analysis():
    try:
        data = compute_trend_metrics()
        return sanitize(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Trend analysis failed: {str(e)}")
