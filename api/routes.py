from fastapi import APIRouter, HTTPException
from scripts.ride_database import (
    get_all_rides,
    get_ride_by_id,
    get_all_ride_summaries
)
from scripts.ride_processor import process_latest_fit_file
from scripts.fetch_fit_from_dropbox import backfill_ride_history
from scripts.trend_analysis import generate_trend_analysis
from scripts.dropbox_auth import refresh_dropbox_token

router = APIRouter()

@router.get("/latest-ride-data")
def latest_ride_data():
    """
    Process and return the most recent ride's summary and full data.
    """
    try:
        summary, full_data = process_latest_fit_file()
        return {"summary": summary, "full_data": full_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process latest ride: {e}")


@router.get("/ride-history")
def ride_history(summary_only: bool = False):
    """
    Retrieve full or summary ride history from the database.
    """
    try:
        rides = get_all_ride_summaries() if summary_only else get_all_rides()
        return {"rides": rides}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch ride history: {e}")


@router.get("/ride/{ride_id}")
def ride_by_id(ride_id: str):
    """
    Retrieve a specific ride by its unique ride_id.
    """
    try:
        ride = get_ride_by_id(ride_id)
        if not ride:
            raise HTTPException(status_code=404, detail="Ride not found")
        return ride
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch ride: {e}")


@router.get("/trend-analysis")
def trend_analysis():
    """
    Compute CTL, ATL, TSB, FTP trends, and zone breakdown from ride history.
    """
    try:
        return generate_trend_analysis()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Trend analysis failed: {e}")


@router.get("/trend-analysis-safe")
def trend_analysis_safe():
    """
    Trigger full backfill before trend analysis to ensure DB is up-to-date.
    """
    try:
        backfill_ride_history()
        return generate_trend_analysis()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Trend analysis failed during safe sync: {e}")


@router.get("/backfill")
def run_backfill():
    """
    Import all FIT files from Dropbox and store them in the database.
    """
    try:
        result = backfill_ride_history()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Backfill failed: {e}")


@router.get("/refresh-token")
def refresh_token():
    """
    Manually refresh the Dropbox access token using the stored refresh token.
    """
    try:
        return refresh_dropbox_token()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Token refresh failed: {e}")
