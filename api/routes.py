from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from scripts.ride_processor import process_and_store_latest_fit_file
from scripts.ride_database import get_all_rides, get_ride_by_id
from scripts.trend_analysis import compute_trend_metrics
from scripts.sanitize import sanitize

router = APIRouter()

@router.get("/latest-ride-data")
async def get_latest_ride_data():
    try:
        summary = process_and_store_latest_fit_file()
        return JSONResponse(content=sanitize(summary))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process latest ride: {str(e)}")

@router.get("/ride-history")
def ride_history():
    try:
        rides = get_all_rides()
        return {"rides": rides}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve ride history: {str(e)}")

@router.get("/ride/{ride_id}")
def get_ride(ride_id: str):
    try:
        ride = get_ride_by_id(ride_id)
        if ride:
            return ride
        raise HTTPException(status_code=404, detail="Ride not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve ride: {str(e)}")

@router.get("/trend-analysis")
def trend_analysis():
    try:
        trend_data = compute_trend_metrics()
        return sanitize(trend_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Trend analysis failed: {str(e)}")
