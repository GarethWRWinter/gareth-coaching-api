from fastapi import FastAPI, APIRouter, HTTPException
from .database import SessionLocal, engine  # adjust import path
from .ride_processor import (
    process_latest_ride,
    get_ride_history,
)
from sqlalchemy import inspect

app = FastAPI()
router = APIRouter()

@router.get("/latest-ride-data")
def latest_ride():
    try:
        data = process_latest_ride()
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process latest ride: {e!s}")

@router.get("/ride-history")
def ride_history():
    try:
        rides = get_ride_history()
        return rides
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load ride history: {e!s}")

# 🎯 Debug endpoint: inspect your DB schema for the "rides" table
debug_router = APIRouter()

@debug_router.get("/debug-schema/rides")
def debug_schema_rides():
    insp = inspect(engine)
    cols = insp.get_columns("rides")
    return [{"name": c["name"], "type": str(c["type"])} for c in cols]

app.include_router(router)
app.include_router(debug_router)
