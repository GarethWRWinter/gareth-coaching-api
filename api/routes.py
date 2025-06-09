from fastapi import APIRouter, HTTPException
from scripts.ride_processor import process_latest_fit_file, get_all_rides, get_trend_analysis, get_power_trends, detect_and_update_ftp

router = APIRouter()

@router.get("/latest-ride-data")
async def latest_ride_data():
    try:
        ride_summary = process_latest_fit_file()
        return ride_summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process latest ride: {e}")

@router.get("/ride-history")
async def ride_history():
    try:
        rides = get_all_rides()
        return rides
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve ride history: {e}")

@router.get("/trend-analysis")
async def trend_analysis():
    try:
        trends = get_trend_analysis()
        return trends
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve trend analysis: {e}")

@router.get("/power-trends")
async def power_trends():
    try:
        trends = get_power_trends()
        return trends
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve power trends: {e}")

@router.get("/ftp-update")
async def ftp_update():
    try:
        update = detect_and_update_ftp()
        return update
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to detect/update FTP: {e}")
