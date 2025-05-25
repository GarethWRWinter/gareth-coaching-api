from fastapi import APIRouter, HTTPException
from scripts.ride_processor import process_latest_fit_file
from scripts.save_latest_ride_to_db import save_latest_ride_to_db
from scripts.ride_database import get_all_rides, get_ride_by_id
from scripts.trend_analysis import generate_trend_analysis
from scripts.dropbox_auth import refresh_dropbox_token

router = APIRouter()

@router.get("/latest-ride-data")
def get_latest_ride_data():
    try:
        access_token = refresh_dropbox_token()
        summary, full_data = process_latest_fit_file(access_token)
        return {"summary": summary, "data": full_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process latest ride: {str(e)}")

@router.get("/save-latest-ride")
def save_latest_ride():
    try:
        summary = save_latest_ride_to_db()
        return {"message": "Ride saved successfully", "summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save ride: {str(e)}")

@router.get("/ride-history")
def ride_history():
    return {"rides": get_all_rides()}

@router.get("/ride/{ride_id}")
def get_ride(ride_id: str):
    ride = get_ride_by_id(ride_id)
    if ride:
        return ride
    raise HTTPException(status_code=404, detail="Ride not found")

@router.get("/trend-analysis")
def trend_analysis():
    return generate_trend_analysis()
