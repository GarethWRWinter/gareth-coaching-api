# api/routes.py

from fastapi import APIRouter, HTTPException
from scripts.ride_processor import process_latest_fit_file
from scripts.ride_database import get_ride_history

router = APIRouter()

@router.get("/latest-ride-data")
def latest_ride_data(ftp: float):
    filepath = "/mnt/data/latest.fit"
    try:
        ride = process_latest_fit_file(filepath, ftp)
        return ride
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process latest ride: {e}")

@router.get("/ride-history")
def ride_history():
    try:
        rides = get_ride_history()
        return [
            {
                "ride_id": r.ride_id,
                "start_time": r.start_time.isoformat(),
                "duration_sec": r.duration_sec,
                "distance_km": r.distance_km,
                "avg_power": r.avg_power,
                "avg_hr": r.avg_hr,
                "avg_cadence": r.avg_cadence,
                "max_power": r.max_power,
                "max_hr": r.max_hr,
                "max_cadence": r.max_cadence,
                "total_work_kj": r.total_work_kj,
                "tss": r.tss,
                "left_right_balance": r.left_right_balance,
                "power_zone_times": r.power_zone_times,
                "normalized_power": r.normalized_power,
            } for r in rides
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch ride history: {e}")
