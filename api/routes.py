from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from scripts.fetch_and_parse import process_latest_fit_file
from scripts.ride_database import get_all_rides, get_ride_by_id, store_ride
from scripts.trend_analysis import compute_trend_metrics
from scripts.sanitize import sanitize

router = APIRouter()

@router.get("/latest-ride-data")
async def get_latest_ride_data():
    try:
        summary = process_latest_fit_file()
        full_data = summary.pop("full_data")
        store_ride(summary, full_data)
        return JSONResponse(content=sanitize({**summary, "full_data": full_data}))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process latest ride: {str(e)}")

@router.get("/trend-analysis")
def get_trend_analysis():
    try:
        result = compute_trend_metrics()
        return JSONResponse(content=sanitize(result))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Trend analysis failed: {str(e)}")

@router.get("/ride-history")
def ride_history():
    try:
        rides = get_all_rides()
        return {"rides": sanitize(rides)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ride history fetch failed: {str(e)}")

@router.get("/ride/{ride_id}")
def ride_by_id(ride_id: str):
    try:
        ride = get_ride_by_id(ride_id)
        if not ride:
            raise HTTPException(status_code=404, detail="Ride not found")
        return JSONResponse(content=sanitize(ride))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ride fetch failed: {str(e)}")
