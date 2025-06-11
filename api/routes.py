from fastapi import APIRouter
from scripts.ride_processor import process_latest_fit_file, get_all_rides

router = APIRouter()

@router.get("/latest-ride-data")
def latest_ride_data():
    try:
        # supply correct FTP and path
        result = process_latest_fit_file("/mnt/data/latest.fit", ftp=250.0)
        return result
    except Exception as e:
        return {"detail": f"Failed to process latest ride: {e}"}

@router.get("/ride-history")
def ride_history():
    try:
        return get_all_rides()
    except Exception as e:
        return {"detail": f"Failed to fetch ride history: {e}"}
