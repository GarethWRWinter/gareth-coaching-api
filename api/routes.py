from fastapi import APIRouter, HTTPException
from scripts.fetch_and_parse import process_latest_fit_file
from scripts.save_latest_ride_to_db import store_ride
from scripts.ride_database import get_all_rides, get_ride_by_id
from scripts.trend_analysis import generate_trend_analysis

router = APIRouter()

@router.get("/latest-ride-data")
def latest_ride_data():
    try:
        summary, full_data = process_latest_fit_file()
        store_ride(summary, full_data)
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process latest ride: {str(e)}")

@router.get("/ride-history")
def ride_history():
    try:
        rides = get_all_rides()
        return {"rides": rides}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ride/{ride_id}")
def specific_ride(ride_id: str):
    try:
        ride = get_ride_by_id(ride_id)
        if ride is None:
            raise HTTPException(status_code=404, detail="Ride not found")
        return ride
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/trend-analysis")
def trend_analysis():
    try:
        return generate_trend_analysis()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
