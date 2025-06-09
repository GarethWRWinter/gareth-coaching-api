from sqlalchemy.orm import Session
from scripts.models import Ride  # ✅ Correct import now
from scripts.database import SessionLocal


def get_latest_ride():
    session = SessionLocal()
    try:
        ride = session.query(Ride).order_by(Ride.start_time.desc()).first()
        return ride
    finally:
        session.close()


def get_ride_history(limit: int = 10):
    session = SessionLocal()
    try:
        rides = session.query(Ride).order_by(Ride.start_time.desc()).limit(limit).all()
        return rides
    finally:
        session.close()
