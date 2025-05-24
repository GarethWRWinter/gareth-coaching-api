# scripts/analyze_zones_and_store.py

import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
from models import Base, TimeInZone, HRTimeInZone
from sqlalchemy.orm import sessionmaker

load_dotenv()

DATABASE_URL = "sqlite:///ride_data.db"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

def load_latest_ride():
    df = pd.read_csv("latest_ride.csv")
    return df

def calculate_time_in_power_zones(df):
    ftp_row = session.query(TimeInZone).order_by(TimeInZone.id.desc()).first()
    ftp = 265.0  # Replace with real FTP fetching logic later

    power_zones = {
        "Z1 Active Recovery": (0, 0.55 * ftp),
        "Z2 Endurance": (0.55 * ftp, 0.75 * ftp),
        "Z3 Tempo": (0.75 * ftp, 0.90 * ftp),
        "Z4 Threshold": (0.90 * ftp, 1.05 * ftp),
        "Z5 VO2 Max": (1.05 * ftp, 1.20 * ftp),
        "Z6 Anaerobic": (1.20 * ftp, 1.50 * ftp),
        "Z7 Neuromuscular": (1.50 * ftp, float("inf")),
    }

    zone_durations = {zone: 0 for zone in power_zones}
    for _, row in df.iterrows():
        power = row.get("power")
        if pd.isna(power):
            continue
        for zone, (low, high) in power_zones.items():
            if low <= power < high:
                zone_durations[zone] += 1
                break
    return zone_durations

def calculate_time_in_hr_zones(df):
    hr_zones = {
        "HR1 Recovery": (0, 114),
        "HR2 Endurance": (114, 133),
        "HR3 Tempo": (133, 152),
        "HR4 Threshold": (152, 171),
        "HR5 Max": (171, float("inf")),
    }

    zone_durations = {zone: 0 for zone in hr_zones}
    for _, row in df.iterrows():
        hr = row.get("heart_rate")
        if pd.isna(hr):
            continue
        for zone, (low, high) in hr_zones.items():
            if low <= hr < high:
                zone_durations[zone] += 1
                break
    return zone_durations

# Main process
df = load_latest_ride()
filename = df["filename"].iloc[0] if "filename" in df.columns else "unknown.fit"

# Power zones
power_zone_data = []
for name, duration in calculate_time_in_power_zones(df).items():
    power_zone_data.append(TimeInZone(zone=name, duration_seconds=duration, filename=filename))
session.add_all(power_zone_data)

# HR zones
hr_zone_data = []
for name, duration in calculate_time_in_hr_zones(df).items():
    hr_zone_data.append(HRTimeInZone(zone=name, duration_seconds=duration, filename=filename))
session.add_all(hr_zone_data)

session.commit()
print(f"✅ Saved power + HR zones for {filename} to the database.")
