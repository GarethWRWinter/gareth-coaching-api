# scripts/ftp_detection.py

from scripts.ride_database import get_all_rides, SessionLocal, Ride
from sqlalchemy.orm import Session

def detect_and_update_ftp():
    rides = get_all_rides()
    if not rides:
        return {"message": "No rides available to calculate FTP."}

    # Search for the highest 20-min power
    max_20min_power = 0.0
    for ride in rides:
        if ride.power_zone_times and "seconds" in ride.power_zone_times:
            seconds_data = ride.power_zone_times["seconds"]
            if seconds_data:
                for duration, value in seconds_data.items():
                    if duration == "1200":  # 20-min power in seconds
                        if value > max_20min_power:
                            max_20min_power = value

    if max_20min_power == 0.0:
        return {"message": "No 20-min best effort found to calculate FTP."}

    # Calculate FTP (95% of best 20-min power)
    new_ftp = round(max_20min_power * 0.95, 2)

    # Update FTP in a 'settings' table (or a dedicated field if exists)
    db: Session = SessionLocal()
    try:
        # Check if FTP already exists
        setting = db.query(Ride).filter(Ride.ride_id == "FTP_SETTING").first()
        if setting:
            # Only update if new FTP is higher
            current_ftp = float(setting.avg_power)
            if new_ftp > current_ftp:
                setting.avg_power = new_ftp
                db.commit()
                return {"new_ftp": new_ftp, "message": "FTP updated."}
            else:
                return {"message": "No new FTP detected; current FTP is sufficient."}
        else:
            # Create a new FTP record
            ftp_setting = Ride(
                ride_id="FTP_SETTING",
                avg_power=new_ftp
            )
            db.add(ftp_setting)
            db.commit()
            return {"new_ftp": new_ftp, "message": "FTP record created."}
    finally:
        db.close()
