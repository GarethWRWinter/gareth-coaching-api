import json
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

    ride_data = sanitize(latest_ride.__dict__)
    
    # Parse power_zone_times back to dict if it's a JSON string
    if ride_data.get("power_zone_times") and isinstance(ride_data["power_zone_times"], str):
        ride_data["power_zone_times"] = json.loads(ride_data["power_zone_times"])

    return ride_data


def get_ride_history():
    db: Session = SessionLocal()
    rides = db.query(Ride).order_by(Ride.start_time.desc()).all()
    db.close()

    ride_list = []
    for ride in rides:
        ride_data = sanitize(ride.__dict__)
        if ride_data.get("power_zone_times") and isinstance(ride_data["power_zone_times"], str):
            ride_data["power_zone_times"] = json.loads(ride_data["power_zone_times"])
        ride_list.append(ride_data)

    return ride_list


def get_all_rides():
    db: Session = SessionLocal()
    rides = db.query(Ride).all()
    db.close()

    ride_list = []
    for ride in rides:
        ride_data = sanitize(ride.__dict__)
        if ride_data.get("power_zone_times") and isinstance(ride_data["power_zone_times"], str):
            ride_data["power_zone_times"] = json.loads(ride_data["power_zone_times"])
        ride_list.append(ride_data)

    return ride_list


def store_ride(ride_data: dict):
    """
    Stores a new ride record in the database, ignoring if the ride_id already exists.
    Uses Postgres ON CONFLICT DO NOTHING to avoid duplicate key errors.
    Ensures all bind parameters have a value (None if missing) and serializes JSON fields.
    """
    db: Session = SessionLocal()

    required_keys = [
        "ride_id", "start_time", "duration_sec", "distance_km",
        "avg_power", "avg_hr", "avg_cadence", "max_power", "max_hr", "max_cadence",
        "total_work_kj", "tss", "normalized_power", "left_right_balance", "power_zone_times"
    ]
    for key in required_keys:
        if key not in ride_data:
            ride_data[key] = None

    # Convert power_zone_times dict to JSON string if not None
    if ride_data["power_zone_times"] is not None:
        ride_data["power_zone_times"] = json.dumps(ride_data["power_zone_times"])

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
