import sqlite3
import json
import os
from datetime import datetime

DB_PATH = "ride_data.db"

def initialize_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rides (
            ride_id TEXT PRIMARY KEY,
            start_time TEXT,
            duration_sec INTEGER,
            distance_km REAL,
            avg_power REAL,
            avg_heart_rate REAL,
            avg_cadence REAL,
            max_power REAL,
            max_heart_rate REAL,
            max_cadence REAL,
            normalized_power REAL,
            intensity_factor REAL,
            tss REAL,
            zone_durations TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def store_ride(ride_summary):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    zone_durations_json = json.dumps(ride_summary.get("zone_durations", {}))

    cursor.execute("""
        INSERT OR REPLACE INTO rides (
            ride_id,
            start_time,
            duration_sec,
            distance_km,
            avg_power,
            avg_heart_rate,
            avg_cadence,
            max_power,
            max_heart_rate,
            max_cadence,
            normalized_power,
            intensity_factor,
            tss,
            zone_durations,
            created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        ride_summary["ride_id"],
        ride_summary["start_time"],
        ride_summary["duration_sec"],
        ride_summary["distance_km"],
        ride_summary["avg_power"],
        ride_summary["avg_heart_rate"],
        ride_summary["avg_cadence"],
        ride_summary["max_power"],
        ride_summary["max_heart_rate"],
        ride_summary["max_cadence"],
        ride_summary["normalized_power"],
        ride_summary["intensity_factor"],
        ride_summary["tss"],
        zone_durations_json,
        datetime.utcnow().isoformat()
    ))

    conn.commit()
    conn.close()

def get_all_rides():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM rides ORDER BY start_time DESC")
    rows = cursor.fetchall()
    conn.close()

    columns = [
        "ride_id", "start_time", "duration_sec", "distance_km", "avg_power",
        "avg_heart_rate", "avg_cadence", "max_power", "max_heart_rate",
        "max_cadence", "normalized_power", "intensity_factor", "tss",
        "zone_durations", "created_at"
    ]

    return [dict(zip(columns, row)) for row in rows]

def get_ride(ride_id: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM rides WHERE ride_id = ?", (ride_id,))
    row = cursor.fetchone()
    conn.close()

    if row is None:
        raise ValueError(f"No ride found with ride_id: {ride_id}")

    columns = [
        "ride_id", "start_time", "duration_sec", "distance_km", "avg_power",
        "avg_heart_rate", "avg_cadence", "max_power", "max_heart_rate",
        "max_cadence", "normalized_power", "intensity_factor", "tss",
        "zone_durations", "created_at"
    ]
    return dict(zip(columns, row))
