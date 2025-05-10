import os
import sqlite3
from datetime import datetime
import pandas as pd
from scripts.get_latest_dropbox_file import get_latest_dropbox_file
from scripts.parse_fit_to_df import fitfile_to_dataframe
from scripts.calculate_power_zones import calculate_power_zones

DB_PATH = "ride_data.db"

def save_latest_ride_to_db(access_token: str) -> dict:
    dropbox_folder = os.environ.get("DROPBOX_FOLDER", "")
    latest_file = get_latest_dropbox_file(access_token, dropbox_folder)
    print(f"[INFO] Latest file: {latest_file.name}")

    df = fitfile_to_dataframe(latest_file.name, access_token)
    print(f"[INFO] Parsed {len(df)} rows of ride data.")

    if df.empty:
        print("[ERROR] Dataframe is empty.")
        return {"error": "No data found in FIT file."}

    timestamp = df["timestamp"].iloc[0]
    duration_s = (df["timestamp"].iloc[-1] - df["timestamp"].iloc[0]).total_seconds()
    avg_power = df["power"].mean()
    max_power = df["power"].max()
    avg_hr = df["heart_rate"].mean()
    max_hr = df["heart_rate"].max()

    ftp = 308  # Fixed FTP for now
    intensity_factor = (avg_power / ftp)
    tss = (duration_s * (intensity_factor ** 2)) / 36  # Correct TSS calc

    # Time in zones
    zone_times = calculate_power_zones(df["power"], ftp)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rides (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            rows INTEGER,
            timestamp TEXT,
            duration_s REAL,
            avg_power REAL,
            max_power REAL,
            avg_heart_rate REAL,
            max_heart_rate REAL,
            tss REAL,
            z1 INTEGER,
            z2 INTEGER,
            z3 INTEGER,
            z4 INTEGER,
            z5 INTEGER,
            z6 INTEGER,
            z7 INTEGER,
            UNIQUE(filename, timestamp)
        )
    """)
    conn.commit()

    cursor.execute("""
        INSERT OR IGNORE INTO rides (
            filename, rows, timestamp, duration_s,
            avg_power, max_power, avg_heart_rate,
            max_heart_rate, tss,
            z1, z2, z3, z4, z5, z6, z7
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        latest_file.name,
        len(df),
        timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        duration_s,
        round(avg_power, 1),
        round(max_power, 1),
        round(avg_hr, 1),
        round(max_hr, 1),
        round(tss, 1),
        zone_times["Z1"],
        zone_times["Z2"],
        zone_times["Z3"],
        zone_times["Z4"],
        zone_times["Z5"],
        zone_times["Z6"],
        zone_times["Z7"]
    ))
    conn.commit()
    conn.close()

    return {
        "filename": latest_file.name,
        "rows": len(df),
        "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        "duration_s": int(duration_s),
        "avg_power": round(avg_power, 1),
        "max_power": round(max_power, 1),
        "avg_heart_rate": round(avg_hr, 1),
        "max_heart_rate": round(max_hr, 1),
        "tss": round(tss, 1),
        "time_in_zones": zone_times
    }
