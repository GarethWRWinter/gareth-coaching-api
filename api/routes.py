from fastapi import APIRouter, HTTPException, Query
from scripts.ride_processor import (
    process_latest_fit_file,
    get_all_rides,
    get_trend_analysis,
    get_power_trends,
    detect_and_update_ftp,
    get_ride_by_id
)

router = APIRouter()

@router.get("/latest-ride-data")
def latest_ride_data(ftp: float = Query(..., description="Current FTP in watts")):
    try:
        filepath = "fit_files_latest/latest.fit"  # expected path after Dropbox fetch
        ride_summary = process_latest_fit_file(filepath, ftp)
        return ride_summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ride-history")
def ride_history():
    try:
        return {"rides": get_all_rides()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch ride history: {str(e)}")

@router.get("/trend-analysis")
def trend_analysis():
    try:
        return get_trend_analysis()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Trend analysis failed: {str(e)}")

@router.get("/power-trends")
def power_trends():
    try:
        return get_power_trends()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Power trends failed: {str(e)}")

@router.get("/ftp-update")
def ftp_update():
    try:
        return detect_and_update_ftp()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"FTP update failed: {str(e)}")

@router.get("/ride/{ride_id}")
def ride_by_id(ride_id: str):
    try:
        return get_ride_by_id(ride_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ride fetch failed: {str(e)}")
