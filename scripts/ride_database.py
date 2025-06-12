# scripts/ride_database.py

import os
import json
from sqlalchemy import create_engine, Column, Integer, Float, String, JSON, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from scripts.constants import FTP_DEFAULT

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise EnvironmentError("DATABASE_URL environment variable not set.")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Ride(Base):
    __tablename__ = 'rides'

    id = Column(Integer, primary_key=True, index=True)
    ride_id = Column(String, unique=True, index=True)
    start_time = Column(DateTime, nullable=True)
    duration_sec = Column(Integer)
    distance_km = Column(Float)
    avg_power = Column(Float)
    max_power = Column(Float)
    avg_hr = Column(Float)
    max_hr = Column(Float)
    avg_cadence = Column(Float)
    max_cadence = Column(Float)
    total_work_kj = Column(Float)
    tss = Column(Float)
    left_right_balance = Column(String)
    normalized_power = Column(Float)
    power_zone_times = Column(JSON)
    ftp_used = Column(Float, default=FTP_DEFAULT)
    extra = Column(JSON, nullable=True)

def initialize_database():
    Base.metadata.create_all(bind=engine)

def store_ride(ride_metrics: dict):
    session = SessionLocal()
    try:
        ride = Ride(
            ride_id=ride_metrics.get("ride_id"),
            start_time=ride_metrics.get("start_time", datetime.utcnow()),
            duration_sec=ride_metrics.get("duration_sec"),
            distance_km=ride_metrics.get("distance_km"),
            avg_power=ride_metrics.get("avg_power"),
            max_power=ride_metrics.get("max_power"),
            avg_hr=ride_metrics.get("avg_hr"),
            max_hr=ride_metrics.get("max_hr"),
            avg_cadence=ride_metrics.get("avg_cadence"),
            max_cadence=ride_metrics.get("max_cadence"),
            total_work_kj=ride_metrics.get("total_work_kj"),
            tss=ride_metrics.get("tss"),
            left_right_balance=ride_metrics.get("left_right_balance"),
            normalized_power=ride_metrics.get("normalized_power"),
            power_zone_times=ride_metrics.get("power_zone_times"),
            ftp_used=ride_metrics.get("ftp", FTP_DEFAULT),
            extra=ride_metrics.get("extra", None)
        )
        session.add(ride)
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        raise RuntimeError(f"Failed to store ride: {e}")
    finally:
        session.close()

def get_ride_history():
    session = SessionLocal()
    try:
        rides = session.query(Ride).order_by(Ride.start_time.desc()).all()
        ride_list = []
        for ride in rides:
            ride_list.append({
                "id": ride.id,
                "ride_id": ride.ride_id,
                "start_time": ride.start_time.isoformat() if ride.start_time else None,
                "duration_sec": ride.duration_sec,
                "distance_km": ride.distance_km,
                "avg_power": ride.avg_power,
                "max_power": ride.max_power,
                "avg_hr": ride.avg_hr,
                "max_hr": ride.max_hr,
                "avg_cadence": ride.avg_cadence,
                "max_cadence": ride.max_cadence,
                "total_work_kj": ride.total_work_kj,
                "tss": ride.tss,
                "left_right_balance": ride.left_right_balance,
                "normalized_power": ride.normalized_power,
                "power_zone_times": ride.power_zone_times,
                "ftp_used": ride.ftp_used,
                "extra": ride.extra
            })
        return ride_list
    except SQLAlchemyError as e:
        raise RuntimeError(f"Failed to fetch ride history: {e}")
    finally:
        session.close()

def get_ride_by_id(ride_id: str):
    session = SessionLocal()
    try:
        ride = session.query(Ride).filter(Ride.ride_id == ride_id).first()
        if not ride:
            return None
        return {
            "id": ride.id,
            "ride_id": ride.ride_id,
            "start_time": ride.start_time.isoformat() if ride.start_time else None,
            "duration_sec": ride.duration_sec,
            "distance_km": ride.distance_km,
            "avg_power": ride.avg_power,
            "max_power": ride.max_power,
            "avg_hr": ride.avg_hr,
            "max_hr": ride.max_hr,
            "avg_cadence": ride.avg_cadence,
            "max_cadence": ride.max_cadence,
            "total_work_kj": ride.total_work_kj,
            "tss": ride.tss,
            "left_right_balance": ride.left_right_balance,
            "normalized_power": ride.normalized_power,
            "power_zone_times": ride.power_zone_times,
            "ftp_used": ride.ftp_used,
            "extra": ride.extra
        }
    except SQLAlchemyError as e:
        raise RuntimeError(f"Failed to fetch ride by ID: {e}")
    finally:
        session.close()
