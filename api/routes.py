from fastapi import APIRouter, HTTPException, Query
from scripts.ride_database import get_all_rides, get_ride_by_id
from scripts.coach_notes import generate_coach_notes

router = APIRouter()

@router.get("/ride-history")
def get_ride_history():
    try:
        return get_all_rides()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ride/{ride_id}/coach-notes")
def get_coach_notes(ride_id: str):
    try:
        if ride_id == "latest":
            rides = get_all_rides()
            if not rides:
                raise HTTPException(status_code=404, detail="No rides found.")
            ride_id = rides[-1]["ride_id"]
        ride = get_ride_by_id(ride_id)
        if not ride:
            raise HTTPException(status_code=404, detail="Ride not found")
        notes = generate_coach_notes(ride)
        return notes
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
