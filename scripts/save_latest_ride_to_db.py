# scripts/save_latest_ride_to_db.py

from scripts.ride_database import store_ride

def save_ride_to_db(summary: dict, full_data: list) -> None:
    store_ride(summary, full_data)
