from fastapi import APIRouter
from scripts.ride_processor import process_latest_fit_file
from scripts.fetch_and_parse import fetch_latest_fit_file

router = APIRouter()

@router.get("/latest-ride-data")
def latest_ride_data():
    fit_file = fetch_latest_fit_file()
    summary = process_latest_fit_file(fit_file)
    return summary
