from fastapi import APIRouter
from fastapi.responses import JSONResponse
from scripts.save_latest_ride_to_db import process_latest_fit_file
from scripts.dropbox_auth import refresh_access_token
from models.pydantic_models import RideSummary

router = APIRouter()

@router.get("/latest-ride-data", response_model=RideSummary)
def get_latest_ride_data():
    access_token = refresh_access_token()
    result = process_latest_fit_file(access_token)
    return JSONResponse(content=result)
