from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse

from scripts.fetch_and_parse import process_latest_fit_file
from scripts.ride_database import get_all_rides, get_ride_by_id, get_all_ride_summaries
from scripts.trend_analysis import compute_trend_metrics
from scripts.sanitize import sanitize
from scripts.fetch_fit_from_dropbox import backfill_ride_history

router = APIRouter()

@router.get("/latest-ride-data")
def get_latest_ride_data():
    try:
        summary, _ = process_latest_fit_file()
        return JSONResponse(content=summary)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process latest ride: {str(e)}")

@router.get("/ride-history")
def ride_history(summary_only: bool = Query(False, description="Only return summary metrics (no full_data)")):
    try:
        rides = get_all_rides()
        if summary_only:
            for ride in rides:
                ride.pop("full_data", None)
        return JSONResponse(content=sanitize({"rides": rides}))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch ride history: {str(e)}")

@router.get("/ride/{ride_id}")
def get_ride(ride_id: str):
    try:
        ride = get_ride_by_id(ride_id)
        if ride:
            return JSONResponse(content=sanitize(ride))
        raise HTTPException(status_code=404, detail="Ride not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch ride: {str(e)}")

@router.get("/trend-analysis")
def trend_analysis():
    try:
        data = compute_trend_metrics()
        return JSONResponse(content=sanitize(data))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Trend analysis failed: {str(e)}")

@router.get("/backfill")
def backfill():
    try:
        from scripts.backfill_from_dropbox import run_backfill
        report = run_backfill()
        return JSONResponse(content=report)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Backfill failed: {str(e)}")

@router.get("/trend-analysis-safe")
def trend_analysis_safe():
    try:
        # Step 1: Trigger backfill
        backfill_result = backfill_ride_history()
        if backfill_result.get("total", 0) == 0:
            return {"message": "Backfill completed, but no rides found in Dropbox."}

        # Step 2: Pull rides from database
        ride_summaries = get_all_ride_summaries()
        if not ride_summaries:
            return {"message": "No ride data available for trend analysis."}

        # Step 3: Run analysis
        return JSONResponse(content=sanitize(compute_trend_metrics(ride_summaries)))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Trend analysis safe failed: {str(e)}")
