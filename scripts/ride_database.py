import os
from sqlalchemy import create_engine, Column, Integer, String, Float, JSON, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Ride(Base):
    __tablename__ = "rides"

    id = Column(Integer, primary_key=True, index=True)
    ride_id = Column(String, unique=True, index=True, nullable=False)
    start_time = Column(DateTime)
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
    normalized_power = Column(Float)
    left_right_balance = Column(String)
    power_zone_times = Column(JSON)
    ftp_used = Column(Integer)

def store_ride(data: dict):
    db = SessionLocal()
    ride = Ride(**data)
    db.add(ride)
    db.commit()
    db.refresh(ride)
    db.close()

def get_ride_history():
    db = SessionLocal()
    rides = db.query(Ride).order_by(Ride.start_time.desc()).all()
    db.close()
    return [
        {
            "ride_id": r.ride_id,
            "start_time": r.start_time.isoformat() if r.start_time else None,
            "duration_sec": r.duration_sec,
            "avg_power": r.avg_power,
            "tss": r.tss,
            "ftp_used": r.ftp_used,
            "power_zone_times": r.power_zone_times
        }
        for r in rides
    ]
