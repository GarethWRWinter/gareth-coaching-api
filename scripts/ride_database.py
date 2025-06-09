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


def store_ride(ride_data: dict):
    """
    Stores a new ride record in the database, replacing if the ride_id already exists.
    """
    db: Session = SessionLocal()
    ride = Ride(
        ride_id=ride_data.get("ride_id"),
        start_time=ride_data.get("start_time"),
        duration_sec=ride_data.get("duration_sec"),
        distance_km=ride_data.get("distance_km"),
        avg_power=ride_data.get("avg_power"),
        max_power=ride_data.get("max_power"),
        tss=ride_data.get("tss"),
        total_work_kj=ride_data.get("total_work_kj"),
        power_zone_times=ride_data.get("power_zone_times"),
    )
    # Use merge() for upsert behavior
    db.merge(ride)
    db.commit()
    db.close()
