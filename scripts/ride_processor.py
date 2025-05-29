from scripts.fetch_fit_from_dropbox import get_latest_fit_file_from_dropbox
from scripts.parse_fit import parse_fit
from scripts.fit_metrics import calculate_ride_metrics
from scripts.ride_database import store_ride, get_all_rides, get_ride
from scripts.sanitize import sanitize

def process_latest_fit_file():
    # Download latest .fit file
    local_path = get_latest_fit_file_from_dropbox()

    # Parse .fit to DataFrame
    df = parse_fit(local_path)
    if df is None or df.empty:
        raise ValueError("Parsed DataFrame is empty or invalid")

    # Calculate summary
    ride_summary = calculate_ride_metrics(df)

    # Store in DB
    store_ride(ride_summary, df)

    # Sanitize and return
    return sanitize(ride_summary), df.to_dict(orient="records")

def get_all_ride_summaries():
    all_rides = get_all_rides()
    return sanitize(all_rides)

def get_ride_by_id(ride_id):
    ride = get_ride(ride_id)
    return sanitize(ride)

def backfill_all_rides():
    return {"detail": "Backfill logic not implemented yet."}
