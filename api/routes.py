from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from scripts.save_latest_ride_to_db import save_ride_to_db
from scripts.fetch_and_parse import process_latest_fit_file
from scripts.trend_analysis import compute_trend_metrics
from scripts.ride_database import get_all_rides, get_ride_by_id
from scripts.sanitize import sanitize

router = APIRouter()

@router.get("/latest-ride-data")
async def get_latest_ride_data():
    try:
        summary, full_data = process_latest_fit_file()
        save_ride_to_db(summary, full_data)
        return sanitize(summary)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process latest ride: {str(e)}")

@router.get("/trend-analysis")
def get_trend_analysis():
    try:
        data = compute_trend_metrics()
        return sanitize(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Trend analysis failed: {str(e)}")

@router.get("/ride-history")
def get_ride_history():
    try:
        rides = get_all_rides()
        return {"rides": rides}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch ride history: {str(e)}")

@router.get("/ride/{ride_id}")
def get_specific_ride(ride_id: str):
    try:
        if ride_id == "latest":
            rides = get_all_rides()
            if not rides:
                raise HTTPException(status_code=404, detail="No rides found.")
            ride_id = rides[-1]["ride_id"]

        ride_data = get_ride_by_id(ride_id)
        if not ride_data:
            raise HTTPException(status_code=404, detail="Ride not found.")
        return sanitize(ride_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch ride {ride_id}: {str(e)}")
