# scripts/ftp_tracking.py

from scripts.ride_database import get_ride_history, update_ftp_value
from datetime import datetime
import pandas as pd

CURRENT_FTP = 308  # Default unless updated

def detect_and_update_ftp():
    try:
        rides = get_ride_history()
        if not rides or len(rides) < 1:
            return {"ftp": CURRENT_FTP, "message": "No rides available to analyze FTP."}

        best_20_min_power = 0
        best_ride_id = None

        for ride in rides:
            if not ride.get("power_zone_times"):
                continue
            np = ride.get("normalized_power")
            duration = ride.get("duration_sec", 0)
            avg_power = ride.get("avg_power", 0)

            if duration >= 1200 and avg_power > best_20_min_power:
                best_20_min_power = avg_power
                best_ride_id = ride.get("ride_id")

        estimated_ftp = round(best_20_min_power * 0.95, 1)

        if estimated_ftp > CURRENT_FTP + 3:
            update_ftp_value(estimated_ftp)
            return {
                "ftp": estimated_ftp,
                "message": f"FTP updated from {CURRENT_FTP} to {estimated_ftp} based on ride {best_ride_id}."
            }
        else:
            return {
                "ftp": CURRENT_FTP,
                "message": f"No change: best 20-min effort doesn't justify an update. Best effort: {best_20_min_power}w."
            }

    except Exception as e:
        return {"ftp": CURRENT_FTP, "message": f"Error analyzing FTP: {str(e)}"}
