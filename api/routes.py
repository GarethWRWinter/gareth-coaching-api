# api/routes.py

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from scripts.ride_processor import process_latest_fit_file, get_all_rides
from scripts.ftp_manager import load_ftp, set_ftp, FTPManagerError
from scripts.ride_database import init_db

router = APIRouter()

# Initialize DB (ensure run at startup in main.py)
init_db()

class FTPUpdate(BaseModel):
    new_ftp: int


@router.get("/ftp")
def get_ftp():
    try:
        current = load_ftp()
    except FTPManagerError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"ftp": current}


@router.post("/ftp")
def update_ftp(payload: FTPUpdate):
    old, new = set_ftp(payload.new_ftp)
    return {"old_ftp": old, "new_ftp": new}


@router.get("/latest-ride-data")
def latest_ride_data(ftp: int = Query(None, description="Optional FTP override")):
    result = process_latest_fit_file(ftp)
    return result


@router.get("/ride-history")
def ride_history():
    try:
        rides = get_all_rides()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"rides": rides}
