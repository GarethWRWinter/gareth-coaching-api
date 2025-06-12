# api/routes.py

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from scripts.dropbox_auth import refresh_dropbox_token
from scripts.ride_processor import (
    process_latest_fit_file,
    get_all_rides,
    get_ride_details
)
from scripts.trend_analysis import calculate_trend_metrics
from scripts.rolling_power import calculate_rolling_power_trends
from scripts.ftp_tracking import detect_and_update_ftp
from scripts.constants import FTP_DEFAULT

router = APIRouter()

@router.get("/latest-ride-data")
def get_latest_ride_data(ftp: float = Query(FTP_DEFAULT, description="Optional FTP override")):
    try:
        access_token = refresh_dropbox_token()
        ride_summary, full_data = process_latest_fit_file(access_token, ftp)
        return {
            "summary": ride_summary,
            "data": full_data
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})

@router.get("/ride-history")
def get_ride_history():
    try:
        rides = get_all_rides()
        return {"rides": rides}
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": f"Failed to fetch ride history: {str(e)}"})

@router.get("/ride/{ride_id}")
def get_specific_ride(ride_id: str):
    try:
        ride = get_ride_details(ride_id)
        return ride
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": f"Failed to fetch ride {ride_id}: {str(e)}"})

@router.get("/trend-analysis")
def get_trend_analysis():
    try:
        trends = calculate_trend_metrics()
        return trends
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": f"Trend analysis error: {str(e)}"})

@router.get("/power-trends")
def get_power_trends():
    try:
        power = calculate_rolling_power_trends()
        return power
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": f"Power trend error: {str(e)}"})

@router.get("/ftp-update")
def get_ftp_update():
    try:
        result = detect_and_update_ftp()
        return result
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": f"FTP update error: {str(e)}"})
