from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import SQLAlchemyError
from models import Base, Ride
import os
import logging

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Determine the database URL from environment or fallback
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///ride_data.db")
logger.info(f"Using DATABASE_URL: {DATABASE_URL}")

# Create engine with appropriate connect_args for SQLite only
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

# Create a scoped session factory
SessionLocal = scoped_session(sessionmaker(bind=engine))

@app.get("/")
def root():
    return {"message": "API is running!"}

@app.get("/latest-ride-data")
def latest_ride_data():
    session = SessionLocal()
    try:
        latest_ride = session.query(Ride).order_by(Ride.start_time.desc()).first()
        if not latest_ride:
            logger.warning("No rides found in database.")
            raise HTTPException(status_code=404, detail="No rides found.")
        # Logging full ride data for debugging
        logger.info(f"Latest ride: {latest_ride.__dict__}")
        return JSONResponse(content={
            "ride_id": latest_ride.ride_id,
            "start_time": str(latest_ride.start_time),
            "duration_sec": latest_ride.duration_sec,
            "normalized_power": latest_ride.normalized_power,
        })
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process latest ride: {str(e)}")
    finally:
        session.close()

@app.get("/ride-history")
def ride_history():
    session = SessionLocal()
    try:
        rides = session.query(Ride).order_by(Ride.start_time.desc()).all()
        if not rides:
            logger.warning("No rides found in database.")
            raise HTTPException(status_code=404, detail="No rides found.")
        # Logging for debugging
        logger.info(f"Fetched {len(rides)} rides.")
        ride_list = [{
            "ride_id": r.ride_id,
            "start_time": str(r.start_time),
            "duration_sec": r.duration_sec,
            "normalized_power": r.normalized_power
        } for r in rides]
        return JSONResponse(content=ride_list)
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch ride history: {str(e)}")
    finally:
        session.close()
