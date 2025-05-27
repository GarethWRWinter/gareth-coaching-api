from fastapi import APIRouter, HTTPException
from scripts.ride_database import get_all_rides, get_ride_by_id, get_all_ride_summaries
from scripts.ride_processor import process_latest_fit_file
from scripts.fetch_fit_from_dropbox import backfill_ride_history
from scripts.trend_analysis import generate_trend_analysis
from scripts.dropbox_auth import refresh_dropbox_token

router = APIRouter()

@router.get("/latest-ride-data")
def latest_ride_data():
    try:
        summary, full_data = process_latest_fit_file()
        return {"summary": summary, "full_data": full_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process latest ride: {e}")

@router.get("/ride-history")
def ride_history(summary_only: bool = False):
    try:
        return {"rides": get_all_ride_summaries() if summary_only else get_all_rides()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch ride history: {e}")

@router.get("/ride/{ride_id}")
def ride_by_id(ride_id: str):
    try:
        ride = get_ride_by_id(ride_id)
        if not ride:
            raise HTTPException(status_code=404, detail="Ride not found")
        return ride
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch ride: {e}")

@router.get("/trend-analysis")
def trend_analysis():
    try:
        return generate_trend_analysis()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Trend analysis failed: {e}")

@router.get("/trend-analysis-safe")
def trend_analysis_safe():
    try:
        backfill_ride_history()
        return generate_trend_analysis()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Trend analysis failed during safe sync: {e}")

@router.get("/backfill")
def run_backfill():
    try:
        result = backfill_ride_history()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Backfill failed: {e}")

@router.get("/refresh-token")
def refresh_token():
    try:
        return refresh_dropbox_token()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Token refresh failed: {e}")
