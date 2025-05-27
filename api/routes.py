from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse

from scripts.ride_database import get_all_rides, get_ride_by_id
from scripts.ride_database import store_ride  # in case we extend later
from scripts.ride_database import initialize_database
from scripts.fetch_and_parse import process_latest_fit_file
from scripts.sanitize import sanitize
from scripts.trend_analysis import compute_trend_metrics
from scripts.dropbox_auth import refresh_dropbox_token
from scripts.fetch_fit_from_dropbox import get_latest_fit_file_from_dropbox
from scripts.backfill_from_dropbox import run_backfill

router = APIRouter()


@router.get("/latest-ride-data")
def latest_ride_data():
    try:
        summary, full_data = process_latest_fit_file()
        return sanitize({
            "summary": summary,
            "full_data": full_data
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process latest ride: {e}")


@router.get("/ride-history")
def ride_history(summary_only: bool = Query(False, description="Only return summary metrics (no full_data)")):
    try:
        rides = get_all_rides()
        if summary_only:
            for ride in rides:
                ride.pop("full_data", None)
        return sanitize({"rides": rides})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch ride history: {e}")


@router.get("/ride/{ride_id}")
def ride_by_id(ride_id: str):
    try:
        summary, seconds = get_ride_by_id(ride_id)
        if not summary:
            raise HTTPException(status_code=404, detail="Ride not found")
        return sanitize({
            "summary": summary,
            "full_data": seconds
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch ride: {e}")


@router.get("/trend-analysis")
def trend_analysis():
    try:
        return sanitize(compute_trend_metrics())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Trend analysis failed: {e}")


@router.get("/trend-analysis-safe")
def trend_analysis_safe():
    try:
        run_backfill()
        return sanitize(compute_trend_metrics())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Trend analysis failed during safe sync: {e}")


@router.get("/backfill")
def trigger_backfill():
    try:
        report = run_backfill()
        return sanitize(report)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Backfill failed: {e}")


@router.get("/refresh-token")
def refresh_token():
    try:
        return sanitize(refresh_dropbox_token())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Token refresh failed: {e}")
