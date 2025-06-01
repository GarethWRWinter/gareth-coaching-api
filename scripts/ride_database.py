# scripts/ride_database.py

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.orm import declarative_base, sessionmaker
import os

DATABASE_URL = os.environ.get("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define the Ride model
class Ride(Base):
    __tablename__ = "rides"

    id = Column(Integer, primary_key=True, index=True)
    ride_id = Column(String, unique=True, index=True)
    start_time = Column(DateTime)
    duration_sec = Column(Integer)
    distance_km = Column(Float)
    avg_power = Column(Float)
    avg_hr = Column(Float)
    avg_cadence = Column(Float)
    max_power = Column(Float)
    max_hr = Column(Float)
    max_cadence = Column(Float)
    total_work_kj = Column(Float)
    tss = Column(Float)
    left_right_balance = Column(String)
    power_zone_times = Column(JSON)

# Initialize the database (create tables if not exist)
def initialize_database():
    Base.metadata.create_all(bind=engine)

# Store a new ride
def store_ride(ride_data: dict):
    db = SessionLocal()
    ride = Ride(**ride_data)
    db.add(ride)
    db.commit()
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
