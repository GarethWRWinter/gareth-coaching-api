from sqlalchemy.orm import Session
from .database import SessionLocal
from .models import Ride
from scripts.sanitize import sanitize


def get_latest_ride():
    db: Session = SessionLocal()
    latest_ride = db.query(Ride).order_by(Ride.start_time.desc()).first()
    db.close()

    if latest_ride is None:
        return {"error": "No rides found"}

    return sanitize(latest_ride.__dict__)


def get_ride_history():
    db: Session = SessionLocal()
    rides = db.query(Ride).order_by(Ride.start_time.desc()).all()
    db.close()

    return [sanitize(ride.__dict__) for ride in rides]


def get_all_rides():
    db: Session = SessionLocal()
    rides = db.query(Ride).all()
    db.close()

    return [sanitize(ride.__dict__) for ride in rides]
