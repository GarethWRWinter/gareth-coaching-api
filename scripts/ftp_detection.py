from scripts.ride_database import get_ride_history


def detect_ftp_change():
    rides = get_ride_history()
    ftp_candidates = []

    for ride in rides:
        # Use dictionary access instead of attribute access
        if ride["normalized_power"] and ride["normalized_power"] > 250:
            ftp_candidates.append({
                "ride_id": ride["ride_id"],
                "normalized_power": ride["normalized_power"],
                "date": ride["start_time"],
            })

    if not ftp_candidates:
        return {"message": "No FTP updates detected."}

    # For demonstration, let's assume the new FTP is the highest normalized power
    new_ftp = max(ftp_candidates, key=lambda r: r["normalized_power"])
    return {
        "message": "New FTP detected.",
        "new_ftp": new_ftp
    }
