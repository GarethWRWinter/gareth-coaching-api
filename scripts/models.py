# scripts/models.py

from sqlalchemy import Column, Integer, String, Float, JSON, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Ride(Base):
    __tablename__ = "rides"

    id = Column(Integer, primary_key=True, index=True)
    ride_id = Column(String, unique=True, index=True)
    start_time = Column(TIMESTAMP, nullable=True)
    duration_sec = Column(Integer, nullable=False)
    distance_km = Column(Float, nullable=True)
    avg_power = Column(Float, nullable=True)
    avg_hr = Column(Float, nullable=True)
    avg_cadence = Column(Float, nullable=True)
    max_power = Column(Float, nullable=True)
    max_hr = Column(Float, nullable=True)
    max_cadence = Column(Float, nullable=True)
    total_work_kj = Column(Float, nullable=True)
    tss = Column(Float, nullable=True)
    normalized_power = Column(Float, nullable=True)
    left_right_balance = Column(JSON, nullable=True)  # if it's JSON; otherwise leave as String
    power_zone_times = Column(JSON, nullable=True)
