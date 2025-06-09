# api/routes.py

from fastapi import APIRouter, HTTPException
from scripts.ride_processor import process_ride_data, get_all_rides
from scripts.dropbox_auth import refresh_dropbox_token
from scripts.trend_analysis import calculate_trend_metrics
from scripts.rolling_power import calculate_rolling_power_trends
from scripts.ftp_detection import detect_and_update_ftp
from scripts.ride_database import get_latest_ride, fetch_latest_ride_data_from_csv

router = APIRouter()


@router.get("/")
def health_check():
    return {"status": "API is live"}


@router.get("/latest-ride-data")
def latest_ride_data():
    """
    Get the most recent ride data.
    If the ride is already processed and in the database, return that.
    Otherwise, parse it dynamically from the latest .fit file.
    """
    try:
        # Fetch the most recent ride data
        latest_ride = get_latest_ride()

        # If no existing ride in DB, fallback to parsing the latest FIT data
        if not latest_ride or latest_ride.get("id") is None:
            # Parse from latest FIT file dynamically
            ride_data_df = fetch_latest_ride_data_from_csv()
            ftp = 308.0  # Use your current FTP dynamically here
            latest_ride = process_ride_data(ride_data_df, ftp)

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
