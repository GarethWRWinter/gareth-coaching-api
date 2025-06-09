# scripts/backfill_np_if_vi.py

import os
import pandas as pd
import json
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from scripts.database import SessionLocal
from scripts.models import Ride
from scripts.sanitize import sanitize

# Load environment variables
load_dotenv()

# FTP constant (update if needed)
FTP = 308.0

def calculate_normalized_power(power_series):
    """
    Normalized Power is the 4th root of the average of 30s rolling average power to the 4th power.
    """
    rolling_avg_30s = power_series.rolling(window=30, min_periods=1).mean()
    rolling_avg_30s_4th = rolling_avg_30s.pow(4)
    mean_rolling_4th = rolling_avg_30s_4th.mean()
    normalized_power = mean_rolling_4th ** 0.25
    return normalized_power

def calculate_if_vi(np, avg_power):
    intensity_factor = np / FTP if FTP and FTP != 0 else None
    variability_index = np / avg_power if avg_power and avg_power != 0 else None
    return intensity_factor, variability_index

def main():
    print("Starting backfill for NP, IF, and VI...")

    # Connect to the DB
    db: Session = SessionLocal()

    # Get all rides
    rides = db.query(Ride).all()
    updated_count = 0

    for ride in rides:
        # Skip if already has NP (assumes if NP is present, IF and VI are too)
        if ride.normalized_power is not None:
            continue

        ride_data_path = f"ride_data/{ride.ride_id.replace('.fit', '.csv')}"
        if not os.path.exists(ride_data_path):
            print(f"Skipping ride {ride.ride_id}: no CSV data found.")
            continue

        df = pd.read_csv(ride_data_path)
        if "power" not in df.columns or df["power"].empty:
            print(f"Skipping ride {ride.ride_id}: no power data.")
            continue

        power_series = df["power"].fillna(0)
        avg_power = power_series.mean()
        np = calculate_normalized_power(power_series)
        if_value, vi_value = calculate_if_vi(np, avg_power)

        # Update the ride in the DB
        update_query = text("""
            UPDATE rides
            SET normalized_power = :np,
                intensity_factor = :if_value,
                variability_index = :vi_value
            WHERE ride_id = :ride_id
        """)
        db.execute(update_query, {
            "np": np,
            "if_value": if_value,
            "vi_value": vi_value,
            "ride_id": ride.ride_id
        })
        updated_count += 1
        print(f"Updated ride {ride.ride_id}: NP={np:.1f}, IF={if_value:.3f}, VI={vi_value:.3f}")

    db.commit()
    db.close()
    print(f"Backfill complete. Updated {updated_count} rides.")

if __name__ == "__main__":
    main()
