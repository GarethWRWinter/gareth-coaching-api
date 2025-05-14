from fastapi import APIRouter
from fastapi.responses import JSONResponse
from scripts.dropbox_auth import refresh_access_token
from scripts.save_latest_ride_to_db import process_latest_fit_file

router = APIRouter()

@router.get("/latest-ride-data")
def get_latest_ride_data():
    access_token = refresh_access_token()
    try:
        result = process_latest_fit_file(access_token)
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Failed to load ride: {str(e)}"})
