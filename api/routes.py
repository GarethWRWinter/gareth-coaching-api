from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from scripts.fetch_and_parse import process_latest_fit_file
from scripts.save_latest_ride_to_db import save_ride_to_db
from scripts.sanitize import sanitize

router = APIRouter()

@router.get("/latest-ride-data")
async def get_latest_ride_data():
    try:
        ride_summary = process_latest_fit_file()
        save_ride_to_db(ride_summary)
        return sanitize(ride_summary)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
