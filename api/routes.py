from fastapi import APIRouter, HTTPException, Query
from scripts.ride_processor import (
    process_latest_fit_file,
    get_ride_by_id,
    get_power_trends,
)
from scripts.ride_database import get_ride_history
from scripts.trend_analysis import get_trend_analysis
from scripts.ftp_tracking import detect_and_optionally_update_ftp

router = APIRouter()


@router.get("/latest-ride-data")
def latest_ride_data(ftp: int = Query(..., description="Current FTP value")):
    try:
        ride_summary, second_by_second_data = process_latest_fit_file(ftp)
        return {
            "summary": ride_summary,
            "second_by_second": second_by_second_data,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process latest ride: {str(e)}")


@router.get("/ride-history")
def ride_history():
    try:
        return get_ride_history()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch ride history: {str(e)}")


@router.get("/ride/{ride_id}")
def ride_by_id(ride_id: str):
    try:
        return get_ride_by_id(ride_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch ride: {str(e)}")


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
        raise HTTPException(status_code=500, detail=f"Failed to compute power trends: {str(e)}")


@router.get("/ftp-update")
def ftp_update():
    try:
        return detect_and_optionally_update_ftp()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"FTP update failed: {str(e)}")
