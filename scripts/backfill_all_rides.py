# scripts/backfill_all_rides.py

import os
import pandas as pd
from scripts.ride_database import save_ride_summary

RIDE_HISTORY_FOLDER = "ride_history"

def load_and_save_all_rides():
    ride_files = [
        f for f in os.listdir(RIDE_HISTORY_FOLDER)
        if f.endswith(".csv")
    ]

    print(f"Found {len(ride_files)} ride history files...")

    for file_name in sorted(ride_files):
        file_path = os.path.join(RIDE_HISTORY_FOLDER, file_name)
        print(f"Processing: {file_name}")
        df = pd.read_csv(file_path)

        if df.empty:
            print(f"⚠️ Skipping empty file: {file_name}")
            continue

        row = df.iloc[0]

        summary = {
            "ride_id": row["ride_id"],
            "timestamp": row["timestamp"],
            "duration": int(row["duration"]),
            "avg_power": float(row["avg_power"]),
            "training_stress_score": float(row["training_stress_score"]),
        }

        save_ride_summary(summary)
        print(f"✅ Saved: {file_name}")

if __name__ == "__main__":
    load_and_save_all_rides()
