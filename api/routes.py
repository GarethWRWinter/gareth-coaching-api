from fastapi import APIRouter, HTTPException
from scripts.ride_processor import (
    process_latest_fit_file,
    get_all_rides,
    get_trend_analysis,
    get_power_trends,
    detect_and_update_ftp
)

router = APIRouter()


@router.get("/latest-ride-data")
def latest_ride_data():
    try:
        filepath = "path/to/latest.fit"  # Replace with your actual logic to get the latest FIT file
        return process_latest_fit_file(filepath)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process latest ride: {str(e)}")


@router.get("/ride-history")
def ride_history():
    return get_all_rides()


@router.get("/trend-analysis")
def trend_analysis():
    return get_trend_analysis()


@router.get("/power-trends")
def power_trends():
    return get_power_trends()


@router.get("/ftp-update")
def ftp_update():
    return detect_and_update_ftp()
