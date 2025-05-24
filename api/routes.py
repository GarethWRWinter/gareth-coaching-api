from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from scripts.fetch_and_parse import process_latest_fit_file
from scripts.save_latest_ride_to_db import save_ride_to_db
from scripts.sanitize import sanitize
import os

router = APIRouter()

@router.get("/latest-ride-data")
async def get_latest_ride_data():
    try:
        access_token = os.getenv("DROPBOX_TOKEN")
        ride_summary = process_latest_fit_file(access_token)
        save_ride_to_db(ride_summary)
        return JSONResponse(content=sanitize(ride_summary))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process latest ride: {str(e)}")
