from scripts.ride_database import get_all_rides

def detect_ftp_change():
    """
    Placeholder logic to detect FTP changes based on past rides.
    Replace with real logic later.
    """
    rides = get_all_rides()
    if not rides:
        return {"ftp_updated": False, "new_ftp": None}

    # Simple example: detect if any ride has NP > 250 as a placeholder threshold
    for ride in rides:
        if ride.normalized_power and ride.normalized_power > 250:
            return {"ftp_updated": True, "new_ftp": ride.normalized_power}

    return {"ftp_updated": False, "new_ftp": None}
