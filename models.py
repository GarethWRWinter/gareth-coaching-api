# models/models.py

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Float, Integer, DateTime, JSON

Base = declarative_base()

class RideData(Base):
    __tablename__ = "rides"

    ride_id = Column(String, primary_key=True, index=True)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    duration_sec = Column(Integer)
    distance_km = Column(Float)
    avg_power = Column(Float)
    max_power = Column(Integer)
    avg_heart_rate = Column(Float)
    max_heart_rate = Column(Integer)
    avg_cadence = Column(Float)
    max_cadence = Column(Integer)
    total_work = Column(Float)
    tss = Column(Float)
    time_in_zones = Column(JSON)

class FTPRecord(Base):
    __tablename__ = "ftp_records"

    id = Column(Integer, primary_key=True, index=True)
    ftp = Column(Float)
    date = Column(DateTime)
