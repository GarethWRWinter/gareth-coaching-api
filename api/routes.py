# api/routes.py

from fastapi import APIRouter, HTTPException
from scripts.ride_processor import process_ride_data
from scripts.ride_database import get_all_rides, get_latest_ride
from scripts.trend_analysis import calculate_trend_metrics
from scripts.rolling_power import calculate_rolling_power_trends
from scripts.ftp_detection import detect_and_update_ftp

router = APIRouter()


@router.get("/")
def health_check():
    return {"status": "API is live"}


@router.get("/latest-ride-data")
def latest_ride_data():
    """
    Get the most recent ride data.
    If the ride is already processed and in the database, return that.
    Otherwise, return a 404 to indicate no data is available.
    """
    try:
        # Fetch the most recent ride data
        latest_ride = get_latest_ride()

        if not latest_ride or latest_ride.get("id") is None:
            raise HTTPException(status_code=404, detail="No ride data found in the database.")

        return latest_ride
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
