from fastapi.responses import JSONResponse
from fastapi import APIRouter
from scripts.save_latest_ride_to_db import save_latest_ride_to_db
from scripts.refresh_access_token import refresh_access_token
import numpy as np

router = APIRouter()

def sanitize(obj):
    if isinstance(obj, dict):
        return {k: sanitize(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize(v) for v in obj]
    elif isinstance(obj, (np.integer, np.floating)):
        return obj.item()
    else:
        return obj

@router.get("/")
def read_root():
    return {"message": "Welcome to the Cycling Coach API"}

@router.get("/latest-ride-data")
def get_latest_ride_data():
    access_token = refresh_access_token()  # ✅ Proper token refresh
    result = save_latest_ride_to_db(access_token)
    clean_result = sanitize(result)  # ✅ Ensure it's JSON serializable
    return JSONResponse(content=clean_result)

@router.get("/rides")
def list_saved_rides():
    import sqlite3
    conn = sqlite3.connect("ride_data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM rides ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    conn.close()
    clean_rows = [sanitize(dict(zip(columns, row))) for row in rows]  # ✅ Also sanitize here
    return JSONResponse(content=clean_rows)
