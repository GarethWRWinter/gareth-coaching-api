from fastapi import APIRouter, HTTPException
from scripts.ride_processor import process_latest_fit_file, get_all_ride_summaries, get_ride_by_id
from scripts.dropbox_auth import refresh_dropbox_token

router = APIRouter()

@router.get("/latest-ride-data")
async def latest_ride_data():
    try:
        # Refresh Dropbox token
        access_token = refresh_dropbox_token()

        # Process the latest ride
        ride_summary, second_by_second_data, _ = process_latest_fit_file(access_token)  # 👈 Adjusted to unpack 3 values

        return {
            "ride_summary": ride_summary,
            "second_by_second_data": second_by_second_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process latest ride: {e}")

@router.get("/ride-history")
async def ride_history():
    try:
        return get_all_ride_summaries()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch ride history: {e}")

@router.get("/ride/{ride_id}")
async def ride_details(ride_id: str):
    try:
        return get_ride_by_id(ride_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch ride details: {e}")
