from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from scripts.fetch_and_parse import process_latest_fit_file
from scripts.save_latest_ride_to_db import save_ride_to_db
from scripts.sanitize import sanitize

router = APIRouter()


@router.get("/latest-ride-data")
async def get_latest_ride_data():
    try:
        # Process the latest ride from Dropbox and extract summary data
        ride_summary = process_latest_fit_file()

        # Store sanitized summary in the database
        save_ride_to_db(ride_summary)

        # Sanitize response before returning to the client/GPT
        return JSONResponse(content=sanitize(ride_summary))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process latest ride: {str(e)}")

# In api/routes.py

from scripts.trend_analysis import compute_trend_metrics

@router.get("/trend-analysis")
def get_trend_analysis():
    try:
        data = compute_trend_metrics()
        return sanitize(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Trend analysis failed: {str(e)}")
