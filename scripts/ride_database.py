from sqlalchemy.orm import Session
from .database import SessionLocal
from .models import Ride

def store_ride(ride_data: dict):
    session = SessionLocal()
    try:
        ride = Ride(**ride_data)
        session.add(ride)
        session.commit()
    finally:
        session.close()

def get_all_rides():
    session = SessionLocal()
    try:
        return session.query(Ride).order_by(Ride.start_time.desc()).all()
    finally:
        session.close()

def get_ride(ride_id: str):
    session = SessionLocal()
    try:
        return session.query(Ride).filter(Ride.ride_id == ride_id).first()
    finally:
        session.close()

def get_latest_ride():
    session = SessionLocal()
    try:
        return session.query(Ride).order_by(Ride.start_time.desc()).first()
    finally:
        session.close()
