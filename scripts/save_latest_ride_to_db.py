import os
import pandas as pd
from scripts.get_latest_dropbox_file import get_latest_fit_file_from_dropbox
from scripts.fitparser import parse_fit_file
from scripts.time_in_zones import calculate_time_in_zones
from scripts.ride_sanitizer import sanitize_for_json
from scripts.ride_database import save_ride_summary
from scripts.dropbox_auth import refresh_access_token
from dotenv import load_dotenv

load_dotenv()

DROPBOX_FOLDER = os.getenv("DROPBOX_FOLDER", "")
FTP = int(os.getenv("FTP", 308))  # Default FTP if not set

def process_latest_fit_file(access_token: str):
    # 1. Get the latest .fit file from Dropbox
    filename, fit_bytes = get_latest_fit_file_from_dropbox(access_token, DROPBOX_FOLDER)
    if not filename or not fit_bytes:
        raise FileNotFoundError("No .fit file found in Dropbox.")

    # 2. Parse the FIT file
    data = parse_fit_file(fit_bytes)

    # 3. Calculate time in zones
    zones = calculate_time_in_zones(data, FTP)

    # 4. Summarize the ride
    summary = {
        "filename": filename,
        "total_seconds": len(data),
        "zones": zones
    }

    # 5. Save ride summary to DB
    save_ride_summary(filename, summary)  # ✅ FIXED LINE

    # 6. Return sanitized data
    return sanitize_for_json({
        "summary": summary,
        "data": data.to_dict(orient="records")
    })
