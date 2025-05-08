import os
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from models import RideData, FTPRecord, Base
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
DATABASE_URL = "sqlite:///ride_data.db"

# Setup DB
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# --- Get current FTP ---
ftp_record = session.query(FTPRecord).order_by(FTPRecord.date.desc()).first()
if ftp_record is None:
    print("❌ No FTP record found. Please set one using ftp_tracking.py.")
    exit()

ftp = ftp_record.ftp
print(f"📌 Using FTP: {ftp} watts")

# --- Get ride data ---
rides = session.query(RideData).all()

updated_count = 0
for ride in rides:
    # Load all power values for this ride from CSV
    filename = ride.filename.replace(".fit", ".csv")
    csv_path = os.path.join("data", filename)

    if not os.path.exists(csv_path):
        print(f"⚠️ CSV not found: {filename}")
        continue

    df = pd.read_csv(csv_path)
    power_series = df.get("power")

    if power_series is None or power_series.isna().all():
        print(f"⚠️ No valid power data for {filename}")
        continue

    power_series = power_series.fillna(0)

    # --- Calculate TSS ---
    duration_hours = len(power_series) / 3600  # seconds to hours
    avg_power = power_series.mean()
    norm_power = (power_series.pow(4).mean()) ** 0.25  # NP = 4th root of avg(P^4)
    intensity_factor = norm_power / ftp
    tss = (duration_hours * intensity_factor**2 * 100)

    # --- Update the DB record ---
    ride.tss = round(tss, 2)
    updated_count += 1

session.commit()
print(f"✅ Updated TSS for {updated_count} rides.")
