# scripts/ride_database.py

import sqlite3
import os
from scripts.sanitize import sanitize

DB_PATH = os.getenv("DATABASE_PATH", "ride_data.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def initialize_database():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rides (
            ride_id TEXT PRIMARY KEY,
            start_time TEXT,
            duration_sec INTEGER,
            avg_power REAL,
            avg_hr REAL,
            tss REAL,
            np REAL,
            intensity REAL,
            time_in_zones TEXT,
            tag TEXT,
            full_data TEXT
        )
    """)
    conn.commit()
    conn.close()

def store_ride(ride_summary: dict, full_data: list[dict]):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO rides (
            ride_id, start_time, duration_sec, avg_power, avg_hr, tss, np, intensity,
            time_in_zones, tag, full_data
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        ride_summary["ride_id"],
        ride_summary.get("start_time"),
        ride_summary.get("duration_sec"),
        ride_summary.get("avg_power"),
        ride_summary.get("avg_hr"),
        ride_summary.get("tss"),
        ride_summary.get("np"),
        ride_summary.get("intensity"),
        str(ride_summary.get("time_in_zones")),
        ride_summary.get("tag", "Unclassified"),
        str(full_data)
    ))

    conn.commit()
    conn.close()

def get_ride_summary_by_id(ride_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM rides WHERE ride_id = ?", (ride_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_all_rides():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT ride_id, start_time, avg_power, tss, duration_sec FROM rides ORDER BY start_time DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_all_rides_with_data():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM rides ORDER BY start_time DESC")
    rows = cursor.fetchall()
    conn.close()

    result = []
    for row in rows:
        ride = dict(row)
        ride["tss"] = float(ride.get("tss") or 0)
        ride["avg_power"] = float(ride.get("avg_power") or 0)
        ride["duration_sec"] = int(ride.get("duration_sec") or 0)
        ride["start_time"] = ride.get("start_time")
        ride["tag"] = ride.get("tag") or "Unclassified"
        result.append(sanitize(ride))

    return result
