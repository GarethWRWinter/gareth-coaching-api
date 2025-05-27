from fastapi import APIRouter, HTTPException, Query
from scripts.ride_processor import process_latest_fit_file, get_all_ride_summaries, get_ride_by_id, backfill_all_rides

router = APIRouter()

@router.get("/latest-ride-data")
def get_latest_ride():
    try:
        full_data, summary = process_latest_fit_file()
        return {
            "ride_summary": summary,
            "ride_data": full_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process latest ride: {str(e)}")

@router.get("/ride-history")
def ride_history(summary_only: bool = Query(default=True)):
    try:
        if summary_only:
            return {"rides": get_all_ride_summaries()}
        else:
            # Returns full second-by-second data for each ride
            return {"rides": get_all_ride_summaries(include_full_data=True)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch ride history: {str(e)}")

@router.get("/ride/{ride_id}")
def get_ride(ride_id: str):
    try:
        data = get_ride_by_id(ride_id)
        if not data:
            raise HTTPException(status_code=404, detail="Ride not found")
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching ride {ride_id}: {str(e)}")

@router.get("/backfill")
def backfill():
    try:
        backfilled, skipped, total = backfill_all_rides()
        return {"backfilled": backfilled, "skipped": skipped, "total": total}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Backfill failed: {str(e)}")
