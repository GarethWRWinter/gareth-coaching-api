import os
import dropbox
import pandas as pd
import sqlite3
from datetime import datetime
from scripts.get_latest_dropbox_file import get_latest_dropbox_file
from scripts.parse_fit_to_df import fitfile_to_dataframe

DB_PATH = "ride_data.db"

def save_latest_ride_to_db(access_token):
    DROPBOX_FOLDER = os.environ.get("DROPBOX_FOLDER", "/Apps/WahooFitness")

    # Connect to Dropbox
    dbx = dropbox.Dropbox(access_token)

    # Get latest .FIT file from Dropbox
    latest_file = get_latest_dropbox_file(dbx, DROPBOX_FOLDER)
    if not latest_file:
        raise Exception("No .FIT files found in Dropbox.")

    print(f"[INFO] Latest file: {latest_file.name}")

    # Download and parse the .FIT file
    metadata, res = dbx.files_download(latest_file.path_lower)
    df = fitfile_to_dataframe(res.content)
    print(f"[INFO] Parsed {len(df)} rows of ride data.")

    # Generate summary
    summary = {
        "filename": latest_file.name,
        "rows": len(df),
        "timestamp": df["timestamp"].min().strftime("%Y-%m-%d %H:%M:%S"),
        "duration_s": int((df["timestamp"].max() - df["timestamp"].min()).total_seconds()),
        "avg_power": round(df["power"].mean(), 1),
        "max_power": round(df["power"].max(), 1),
        "avg_heart_rate": round(df["heart_rate"].mean(), 1),
        "max_heart_rate": round(df["heart_rate"].max(), 1),
        "tss": round((df["power"].mean()**2 * len(df) / 3600) / 100, 1)  # simplified
    }

    # Save to SQLite
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS rides (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            rows INTEGER,
            timestamp TEXT,
            duration_s INTEGER,
            avg_power REAL,
            max_power REAL,
            avg_heart_rate REAL,
            max_heart_rate REAL,
            tss REAL
        )
    """)
    c.execute("""
        INSERT INTO rides (filename, rows, timestamp, duration_s, avg_power, max_power,
                           avg_heart_rate, max_heart_rate, tss)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        summary["filename"],
        summary["rows"],
        summary["timestamp"],
        summary["duration_s"],
        summary["avg_power"],
        summary["max_power"],
        summary["avg_heart_rate"],
        summary["max_heart_rate"],
        summary["tss"]
    ))
    conn.commit()
    conn.close()

    return summary
