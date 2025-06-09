# api/routes.py

from fastapi import APIRouter, HTTPException
from scripts.ride_processor import (
    process_latest_fit_file,
    get_all_rides  # <- FIXED: use get_all_rides, not get_all_ride_summaries
)
from scripts.dropbox_auth import refresh_dropbox_token
from scripts.trend_analysis import calculate_trend_metrics
from scripts.rolling_power import calculate_rolling_power_trends
from scripts.ftp_detection import detect_and_update_ftp

router = APIRouter()

@router.get("/")
def health_check():
    return {"status": "API is live"}

@router.get("/latest-ride-data")
def latest_ride_data():
    try:
        access_token = refresh_dropbox_token()
        if not access_token:
            raise Exception("No access token retrieved from Dropbox refresh.")
        ride_summary = process_latest_fit_file(access_token)
        return ride_summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process latest ride: {str(e)}")

@router.get("/ride-history")
def ride_history():
    try:
        rides = get_all_rides()
        return rides
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch ride history: {str(e)}")

@router.get("/trend-analysis")
def trend_analysis():
    try:
        trends = calculate_trend_metrics()
        return trends
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate trend analysis: {str(e)}")

@router.get("/power-trends")
def power_trends():
    try:
        trends = calculate_rolling_power_trends()
        return trends
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate power trends: {str(e)}")

@router.get("/ftp-update")
def ftp_update():
    try:
        result = detect_and_update_ftp()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update FTP: {str(e)}")
