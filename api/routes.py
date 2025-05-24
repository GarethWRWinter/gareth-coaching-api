from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from scripts.save_latest_ride_to_db import save_ride_to_db
from scripts.trend_analysis import compute_trend_metrics
from scripts.ride_database import get_all_ride_summaries, get_ride_by_id
from scripts.ride_database import initialize_database
from scripts.ride_database import get_ride_summary_by_id
from scripts.ride_database import get_all_ride_ids
from scripts.ride_database import ride_exists
from scripts.ride_database import get_full_ride_by_id
from scripts.ride_processor import process_latest_fit_file
from scripts.sanitize import sanitize
import os

router = APIRouter()

@router.get("/latest-ride-data")
async def get_latest_ride_data():
    try:
        access_token = os.getenv("DROPBOX_TOKEN")
        full_data, summary = process_latest_fit_file(access_token)
        save_ride_to_db(summary, full_data)
        return JSONResponse(content=sanitize(summary))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process latest ride: {str(e)}")

@router.get("/ride-history")
async def get_ride_history():
    try:
        rides = get_all_ride_summaries()
        return {"rides": sanitize(rides)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve ride history: {str(e)}")

@router.get("/ride/{ride_id}")
async def get_ride(ride_id: str):
    try:
        if ride_id == "latest":
            ride_ids = get_all_ride_ids()
            if not ride_ids:
                raise HTTPException(status_code=404, detail="No rides found.")
            ride_id = sorted(ride_ids)[-1]

        if not ride_exists(ride_id):
            raise HTTPException(status_code=404, detail="Ride not found.")

        full_data = get_full_ride_by_id(ride_id)
        summary = get_ride_summary_by_id(ride_id)
        return {"summary": sanitize(summary), "data": sanitize(full_data)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve ride data: {str(e)}")

@router.get("/trend-analysis")
async def trend_analysis():
    try:
        trend_data = compute_trend_metrics()
        return sanitize(trend_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to compute trend analysis: {str(e)}")
