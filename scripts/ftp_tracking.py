# scripts/ftp_tracking.py

from scripts.ride_database import get_ride_history, update_ftp_value

def detect_and_optionally_update_ftp(update: bool = False) -> dict:
    """
    Detect FTP from historical ride data using best 20-minute effort.
    Optionally update the stored FTP value in the database.

    Args:
        update (bool): If True, updates FTP in DB.

    Returns:
        dict: {
            "detected_ftp": int,
            "was_updated": bool
        }
    """
    rides = get_ride_history()
    best_20_min_power = 0

    for ride in rides:
        if "second_by_second" not in ride:
            continue
        powers = [point.get("power", 0) for point in ride["second_by_second"] if point.get("power")]
        if len(powers) < 1200:
            continue
        for i in range(len(powers) - 1200):
            avg_20_min = sum(powers[i:i+1200]) / 1200
            if avg_20_min > best_20_min_power:
                best_20_min_power = avg_20_min

    if best_20_min_power == 0:
        return {"detected_ftp": None, "was_updated": False}

    estimated_ftp = int(round(best_20_min_power * 0.95))
    was_updated = False

    if update:
        update_ftp_value(estimated_ftp)
        was_updated = True

    return {
        "detected_ftp": estimated_ftp,
        "was_updated": was_updated
    }
