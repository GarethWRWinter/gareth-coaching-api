import sqlite3
import os

DB_FILE = os.path.join(os.path.dirname(__file__), "../ride_data.db")

def initialize_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rides (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            duration_minutes REAL,
            distance_km REAL,
            avg_power REAL,
            max_power REAL,
            avg_hr REAL,
            max_hr REAL,
            avg_cadence REAL,
            max_cadence REAL,
            time_in_zones TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_ride_summary(data, summary):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO rides (
            date,
            duration_minutes,
            distance_km,
            avg_power,
            max_power,
            avg_hr,
            max_hr,
            avg_cadence,
            max_cadence,
            time_in_zones
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        summary.get("date"),
        summary.get("duration_minutes"),
        summary.get("distance_km"),
        summary.get("avg_power"),
        summary.get("max_power"),
        summary.get("avg_hr"),
        summary.get("max_hr"),
        summary.get("avg_cadence"),
        summary.get("max_cadence"),
        str(summary.get("time_in_zones"))
    ))
    conn.commit()
    conn.close()
