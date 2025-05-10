from fastapi import APIRouter
from fastapi.responses import JSONResponse
from scripts.save_latest_ride_to_db import save_latest_ride_to_db
from dropbox_auth import get_dropbox_access_token
import sqlite3

router = APIRouter()

@router.get("/")
def read_root():
    return {"message": "Welcome to the Cycling Coach API"}

@router.get("/latest-ride-data")
def get_latest_ride_data():
    access_token = get_dropbox_access_token()
    result = save_latest_ride_to_db(access_token)
    return JSONResponse(content=result)

@router.get("/rides")
def list_saved_rides():
    conn = sqlite3.connect("ride_data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM rides ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    conn.close()
    return JSONResponse(content=[dict(zip(columns, row)) for row in rows])
