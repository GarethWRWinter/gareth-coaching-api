import os
import sqlite3
from datetime import datetime
import pandas as pd
from scripts.get_latest_dropbox_file import get_latest_dropbox_file
from scripts.parse_fit_to_df import fitfile_to_dataframe

DB_PATH = "ride_data.db"

def save_latest_ride_to_db(access_token: str) -> dict:
    dropbox_folder = os.environ.get("DROPBOX_FOLDER", "")
    latest_file = get_latest_dropbox_file(access_token, dropbox_folder)
    print(f"[INFO] Latest file: {latest_file.name}")

    df = fitfile_to_dataframe(latest_file.name, access_token)
    print(f"[INFO] Parsed {len(df)} rows of ride data.")

    timestamp = df["timestamp"].iloc[0]
    duration_s = (df["timestamp"].iloc[-1] - df["timestamp"].iloc[0]).total_seconds()
    avg_power = df["power"].mean()
    max_power = df["power"].max()
    avg_hr = df["heart_rate"].mean()
    max_hr = df["heart_rate"].max()
    tss = (duration_s * avg_power) / 3600  # Approximate Training Stress Score

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
            UNIQUE(filename, timestamp)
        )
    """)
    conn.commit()

    cursor.execute("""
        INSERT OR IGNORE INTO rides (
            filename, rows, timestamp, duration_s,
            avg_power, max_power, avg_heart_rate,
            max_heart_rate, tss
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        latest_file.name,
        len(df),
        timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        duration_s,
        round(avg_power, 1),
        round(max_power, 1),
        round(avg_hr, 1),
        round(max_hr, 1),
        round(tss, 1)
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
        "tss": round(tss, 1)
    }
