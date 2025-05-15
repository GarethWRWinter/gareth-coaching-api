from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from scripts.dropbox_auth import get_valid_access_token
from scripts.save_latest_ride_to_db import process_latest_fit_file
from scripts.ride_database import get_all_ride_summaries, get_ride_by_id

router = APIRouter()

@router.get("/latest-ride-data")
async def get_latest_ride_data():
    access_token = get_valid_access_token()
    result = process_latest_fit_file(access_token)
    return JSONResponse(content=result)

@router.get("/ride-history")
async def ride_history():
    return get_all_ride_summaries()

@router.get("/ride/{ride_id}")
async def ride_detail(ride_id: str):
    data = get_ride_by_id(ride_id)
    if data:
        return JSONResponse(content=data)
    raise HTTPException(status_code=404, detail="Ride not found")

@router.get("/")  # Healthcheck
def healthcheck():
    return {"status": "ok"}
