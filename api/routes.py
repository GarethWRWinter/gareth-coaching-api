# api/routes.py

from fastapi import FastAPI, APIRouter, HTTPException
from sqlalchemy import inspect
from scripts.database import SessionLocal, engine
from scripts.ride_processor import process_latest_ride, get_ride_history

app = FastAPI()
router = APIRouter()

@router.get("/latest-ride-data")
def latest_ride_data():
    session = SessionLocal()
    try:
        data = process_latest_ride(session)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process latest ride: {e}")
    finally:
        session.close()

@router.get("/ride-history")
def ride_history():
    session = SessionLocal()
    try:
        history = get_ride_history(session)
        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch ride history: {e}")
    finally:
        session.close()

# Debug endpoint to inspect the "rides" table schema
debug_router = APIRouter()

@debug_router.get("/debug-schema/rides")
def debug_schema_rides():
    insp = inspect(engine)
    cols = insp.get_columns("rides")
    return [{"name": c["name"], "type": str(c["type"])} for c in cols]

app.include_router(router)
app.include_router(debug_router)
