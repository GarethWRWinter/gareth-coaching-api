from scripts.ride_database import store_ride
from scripts.sanitize import sanitize

def save_ride_to_db(ride_summary: dict):
    sanitized_summary = sanitize(ride_summary)
    store_ride(sanitized_summary)
