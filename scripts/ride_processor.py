# scripts/ride_processor.py

from scripts.ftp_manager import load_ftp
from scripts.ride_database import store_ride, get_ride_history, RideDBError


def process_latest_fit_file(ftp: int | None = None) -> dict:
    """
    Load latest FIT file, process with provided FTP or fallback.
    Returns metrics dict.
    """
    if ftp is None:
        ftp = load_ftp()

    # Implement your FIT parsing logic here (e.g. via fitparse)
    # Example placeholder:
    ride_data = {
        "ride_id": "latest.fit",
        "avg_power": 200,
        "duration_sec": 3600,
        "ftp_used": ftp,
        # ... more fields ...
    }

    # Save to DB
    try:
        store_ride(ride_data)
    except RideDBError as e:
        return {"detail": f"DB storage failed: {e}"}

    return ride_data


def get_all_rides() -> list[dict]:
    """
    Return list of ride info dicts.
    """
    raw = get_ride_history()
    return raw  # already dicts
