from sqlalchemy.orm import Session
from sqlalchemy import text
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
    Stores a new ride record in the database, ignoring if the ride_id already exists.
    Uses Postgres ON CONFLICT DO NOTHING to avoid duplicate key errors.
    """
    db: Session = SessionLocal()
    insert_query = text("""
        INSERT INTO rides (
            ride_id, start_time, duration_sec, distance_km,
            avg_power, avg_hr, avg_cadence, max_power, max_hr, max_cadence,
            total_work_kj, tss, normalized_power, left_right_balance, power_zone_times
        ) VALUES (
            :ride_id, :start_time, :duration_sec, :distance_km,
            :avg_power, :avg_hr, :avg_cadence, :max_power, :max_hr, :max_cadence,
            :total_work_kj, :tss, :normalized_power, :left_right_balance, :power_zone_times
        )
        ON CONFLICT (ride_id) DO NOTHING;
    """)
    db.execute(insert_query, ride_data)
    db.commit()
    db.close()
