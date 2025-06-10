# scripts/models.py

from sqlalchemy import Column, Integer, Float, String, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Ride(Base):
    __tablename__ = 'rides'

    id = Column(Integer, primary_key=True)
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
    normalized_power = Column(Float)  # Retained field
    left_right_balance = Column(String)
    power_zone_times = Column(JSON)   # Already present
    hr_zone_times = Column(JSON)      # Newly added for HR zone breakdown

