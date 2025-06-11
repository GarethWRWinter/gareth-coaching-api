# scripts/ride_database.py

import os
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.exc import SQLAlchemyError

Base = declarative_base()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)

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
    normalized_power = Column(Float)

def store_ride(data: Dict):
    session = SessionLocal()
    try:
        ride = Ride(**data)
        session.add(ride)
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        raise
    finally:
        session.close()

def get_ride_history():
    session = SessionLocal()
    try:
        return session.query(Ride).order_by(Ride.start_time.desc()).all()
    finally:
        session.close()
