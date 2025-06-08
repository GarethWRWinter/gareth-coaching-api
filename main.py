from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import SQLAlchemyError
from models import Base, Ride
import os

app = FastAPI()

# Determine the database URL from environment or fallback
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///ride_data.db")

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
    try:
        session = SessionLocal()
        latest_ride = session.query(Ride).order_by(Ride.start_time.desc()).first()
        if not latest_ride:
            raise HTTPException(status_code=404, detail="No rides found.")
        return JSONResponse(content={
            "ride_id": latest_ride.ride_id,
            "start_time": str(latest_ride.start_time),
            "duration_sec": latest_ride.duration_sec,
            "normalized_power": latest_ride.normalized_power,
        })
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process latest ride: {str(e)}")
    finally:
        session.close()

@app.get("/ride-history")
def ride_history():
    try:
        session = SessionLocal()
        rides = session.query(Ride).order_by(Ride.start_time.desc()).all()
        if not rides:
            raise HTTPException(status_code=404, detail="No rides found.")
        ride_list = [{
            "ride_id": r.ride_id,
            "start_time": str(r.start_time),
            "duration_sec": r.duration_sec,
            "normalized_power": r.normalized_power
        } for r in rides]
        return JSONResponse(content=ride_list)
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch ride history: {str(e)}")
    finally:
        session.close()
