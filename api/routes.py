# api/routes.py
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from scripts.dropbox_auth import refresh_dropbox_token
from scripts.ride_processor import process_latest_fit_file
from scripts.ride_database import get_ride_by_id, get_all_rides
import json

router = APIRouter()

@router.get("/ride-history")
def get_ride_history():
    rides = get_all_rides()
    parsed = []
    for ride in rides:
        if 'summary' in ride:
            try:
                summary = json.loads(ride['summary']) if isinstance(ride['summary'], str) else ride['summary']
                parsed.append(summary)
            except Exception as e:
                print(f"Error parsing ride summary: {e}")
    return parsed

@router.get("/ride/{ride_id}")
def get_ride(ride_id: str):
    if ride_id == "latest":
        access_token = refresh_dropbox_token()
        result = process_latest_fit_file(access_token)
        if "error" in result:
            return JSONResponse(content=result, status_code=500)
        return result
    else:
        ride = get_ride_by_id(ride_id)
        if ride:
            return ride
        return JSONResponse(content={"error": "Ride not found"}, status_code=404)

@router.get("/latest-ride-data")
def get_latest_ride_data():
    access_token = refresh_dropbox_token()
    result = process_latest_fit_file(access_token)
    if "error" in result:
        return JSONResponse(content=result, status_code=500)
    return result

@router.post("/run-backfill")
def run_backfill():
    from scripts.dropbox_utils import list_fit_files_in_folder, download_file
    from scripts.dropbox_auth import refresh_dropbox_token
    from scripts.parse_fit_to_df import parse_fit_file_to_dataframe
    from scripts.sanitize import sanitize_fit_data
    from scripts.fit_metrics import generate_ride_summary
    from scripts.ride_database import save_ride_summary
    import time

    access_token = refresh_dropbox_token()
    fit_files = list_fit_files_in_folder(access_token)
    fit_files.sort()

    results = []

    for path in fit_files:
        filename = path.split("/")[-1]
        try:
            download_file(access_token, path, "temp.fit")
            df = parse_fit_file_to_dataframe("temp.fit")
            df = sanitize_fit_data(df)
            summary = generate_ride_summary(df)
            save_ride_summary(summary)
            results.append({"file": filename, "status": "✅ saved", "ride_id": summary["ride_id"]})
        except Exception as e:
            results.append({"file": filename, "status": "❌ error", "error": str(e)})
        time.sleep(1)

    return {"backfill_summary": results}
