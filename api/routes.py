from fastapi import APIRouter, HTTPException
from scripts.fetch_and_parse import process_latest_fit_file
from scripts.ride_database import get_all_rides, get_ride_by_id
from scripts.save_latest_ride_to_db import save_ride_to_db
from scripts.sanitize import sanitize_fit_data  # ✅ import for response

router = APIRouter()

@router.get("/latest-ride-data")
def get_latest_ride_data():
    try:
        ride_summary = process_latest_fit_file()
        save_ride_to_db(ride_summary)
        return sanitize_fit_data(ride_summary)  # ✅ sanitize before returning
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ride-history")
def ride_history():
    try:
        return get_all_rides()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ride/{ride_id}")
def get_ride(ride_id: str):
    try:
        if ride_id == "latest":
            rides = get_all_rides()
            if not rides:
                raise HTTPException(status_code=404, detail="No rides found.")
            ride_id = sorted(rides, key=lambda x: x['date'], reverse=True)[0]["ride_id"]

        ride = get_ride_by_id(ride_id)
        if not ride:
            raise HTTPException(status_code=404, detail="Ride not found")
        return ride
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
