from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.orm import sessionmaker
import os
from models import Ride  # ✅ Import directly from root-level models.py

DATABASE_URL = os.environ.get("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Initialize the database (create tables if not exist)
def initialize_database():
    Ride.metadata.create_all(bind=engine)

# Store a new ride, avoiding duplicate inserts
def store_ride(ride_data: dict):
    db = SessionLocal()
    try:
        existing_ride = db.query(Ride).filter(Ride.ride_id == ride_data["ride_id"]).first()
        if existing_ride:
            print(f"Ride {ride_data['ride_id']} already exists in the database. Skipping insert.")
            return
        ride = Ride(**ride_data)
        db.add(ride)
        db.commit()
    finally:
        db.close()

# Get all rides
def get_all_rides():
    db = SessionLocal()
    rides = db.query(Ride).order_by(Ride.start_time.desc()).all()
    db.close()
    return rides

# Get a single ride by ID
def get_ride(ride_id: str):
    db = SessionLocal()
    ride = db.query(Ride).filter(Ride.ride_id == ride_id).first()
    db.close()
    return ride
