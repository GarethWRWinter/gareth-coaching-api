# api/routes.py

from fastapi import APIRouter, HTTPException
from scripts.ride_processor import process_latest_fit_file
from scripts.ride_database import get_all_ride_summaries, get_ride_by_id
from scripts.trend_analysis import compute_trend_metrics
from scripts.save_latest_ride_to_db import save_ride_to_db
from scripts.dropbox_auth import refresh_dropbox_token

router = APIRouter()

@router.get("/latest-ride-data")
def latest_ride_data():
    try:
        access_token = refresh_dropbox_token()
        full_data, summary = process_latest_fit_file(access_token=access_token)
        save_ride_to_db(summary, full_data)
        return {"summary": summary, "full_data": full_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process latest ride: {e}")

@router.get("/trend-analysis")
def trend_analysis():
    trends = compute_trend_metrics()
    return trends

@router.get("/ride-history")
def ride_history():
    rides = get_all_ride_summaries()
    return {"rides": rides}

@router.get("/ride/{ride_id}")
def get_ride(ride_id: str):
    ride = get_ride_by_id(ride_id)
    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found")
    return ride
