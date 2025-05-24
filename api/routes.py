from fastapi import APIRouter
from scripts.fetch_and_parse import process_latest_fit_file
from scripts.save_latest_ride_to_db import save_ride_to_db
from scripts.ride_database import get_all_ride_summaries, get_ride_by_id
from scripts.trend_analysis import analyze_trends
from scripts.sanitize import sanitize

router = APIRouter()

@router.get("/latest-ride-data")
def latest_ride_data():
    full_data, summary = process_latest_fit_file()
    save_ride_to_db(summary)  # Only summary is saved
    return {
        "ride_summary": sanitize(summary),
        "ride_data": sanitize(full_data)
    }

@router.get("/trend-analysis")
def trend_analysis():
    return sanitize(analyze_trends())

@router.get("/ride-history")
def ride_history():
    return sanitize(get_all_ride_summaries())

@router.get("/ride/{ride_id}")
def get_ride(ride_id: str):
    return sanitize(get_ride_by_id(ride_id))
