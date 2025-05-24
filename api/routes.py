from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from scripts.fetch_and_parse import process_latest_fit_file
from scripts.save_latest_ride_to_db import save_ride_to_db
from scripts.sanitize import sanitize
from scripts.trend_analysis import compute_trend_metrics
from scripts.ride_database import get_all_rides, get_ride_by_id

router = APIRouter()


@router.get("/latest-ride-data")
async def get_latest_ride_data():
    try:
        ride_summary = process_latest_fit_file()
        save_ride_to_db(ride_summary)
        return JSONResponse(content=sanitize(ride_summary))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process latest ride: {str(e)}")


@router.get("/ride-history")
async def ride_history():
    try:
        rides = get_all_rides()
        return {"rides": sanitize(rides)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch ride history: {str(e)}")


@router.get("/ride/{ride_id}")
async def ride_by_id(ride_id: str):
    try:
        if ride_id == "latest":
            raise HTTPException(status_code=400, detail="Use /latest-ride-data for latest ride")
        ride = get_ride_by_id(ride_id)
        if not ride:
            raise HTTPException(status_code=404, detail="Ride not found")
        return JSONResponse(content=sanitize(ride))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch ride: {str(e)}")


@router.get("/trend-analysis")
def get_trend_analysis():
    try:
        data = compute_trend_metrics()
        return sanitize(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Trend analysis failed: {str(e)}")
