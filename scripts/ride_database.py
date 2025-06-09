from sqlalchemy.orm import Session
from scripts.database import SessionLocal
from scripts.models import Ride

def get_latest_ride():
    with SessionLocal() as session:
        return session.query(Ride).order_by(Ride.start_time.desc()).first()

def get_ride_history():
    with SessionLocal() as session:
        return session.query(Ride).order_by(Ride.start_time.desc()).all()

# 🟩 Alias for compatibility
get_all_rides = get_ride_history
