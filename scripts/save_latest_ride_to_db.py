import os
import sqlite3
from datetime import datetime
import pandas as pd
from scripts.get_latest_dropbox_file import get_latest_dropbox_file
from scripts.parse_fit_to_df import fitfile_to_dataframe

DB_PATH = "ride_data.db"
FTP = 308  # Set your current FTP here

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

    # --- TSS Calculation ---
    normalized_power = df["power"].pow(4).mean() ** 0.25
    intensity_factor = normalized_power / FTP
    tss = (duration_s * normalized_power * intensity_factor) / (FTP * 3600) * 100

    # --- Time in Zones ---
    zone_bounds = [
        (0, 0.55 * FTP),       # Zone 1
        (0.55 * FTP, 0.75 * FTP),  # Zone 2
        (0.75 * FTP, 0.90 * FTP),  # Zone 3
        (0.90 * FTP, 1.05 * FTP),  # Zone 4
        (1.05 * FTP, 1.20 * FTP),  # Zone 5
        (1.20 * FTP, float("inf"))  # Zone 6+
    ]

    time_in_zones = [0] * 6
    for power in df["power"]:
        for i, (low, high) in enumerate(zone_bounds):
            if low <= power < high:
                time_in_zones[i] += 1
                break

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
            zone1_s INTEGER,
            zone2_s INTEGER,
            zone3_s INTEGER,
            zone4_s INTEGER,
            zone5_s INTEGER,
            zone6_s INTEGER,
            UNIQUE(filename, timestamp)
        )
    """)
    conn.commit()

    cursor.execute("""
        INSERT OR IGNORE INTO rides (
            filename, rows, timestamp, duration_s,
            avg_power, max_power, avg_heart_rate,
            max_heart_rate, tss,
            zone1_s, zone2_s, zone3_s, zone4_s, zone5_s, zone6_s
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
        *time_in_zones
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
        "time_in_zones": {
            "zone1_s": time_in_zones[0],
            "zone2_s": time_in_zones[1],
            "zone3_s": time_in_zones[2],
            "zone4_s": time_in_zones[3],
            "zone5_s": time_in_zones[4],
            "zone6_s": time_in_zones[5],
        }
    }
