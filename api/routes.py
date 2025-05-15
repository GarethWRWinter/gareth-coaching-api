from fastapi import APIRouter
from fastapi.responses import JSONResponse
from scripts.dropbox_auth import get_valid_access_token
from scripts.save_latest_ride_to_db import process_latest_fit_file

router = APIRouter()

@router.get("/latest-ride-data")
async def get_latest_ride_data():
    access_token = await get_valid_access_token()
    result = process_latest_fit_file(access_token)
    return JSONResponse(content=result)

@router.get("/")  # Healthcheck
def healthcheck():
    return {"status": "ok"}
