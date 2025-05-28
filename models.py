from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()

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
    left_right_balance = Column(String)  # e.g., "51/49"
    power_zone_times = Column(String)    # JSON string like '{"Z1": 312, "Z2": 430, ...}'

class RideDataPoint(Base):
    __tablename__ = "ride_data"

    id = Column(Integer, primary_key=True, index=True)
    ride_id = Column(String, index=True)
    timestamp = Column(DateTime)
    power = Column(Float)
    heart_rate = Column(Float)
    cadence = Column(Float)
    speed = Column(Float)
    distance = Column(Float)
    left_right_balance = Column(String)  # e.g., "51/49" if captured per point
