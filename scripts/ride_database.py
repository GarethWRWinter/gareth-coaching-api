import sqlite3
import os

DB_PATH = "ride_data.db"

def initialize_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rides (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            duration_sec INTEGER,
            avg_power REAL,
            max_power INTEGER,
            avg_hr REAL,
            max_hr INTEGER,
            avg_cadence REAL,
            max_cadence INTEGER,
            distance_km REAL,
            total_work_kj REAL,
            time_in_zones TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_ride_summary(summary):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO rides (
            date, duration_sec, avg_power, max_power,
            avg_hr, max_hr, avg_cadence, max_cadence,
            distance_km, total_work_kj, time_in_zones
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        summary.get("date"),
        summary.get("duration_sec"),
        summary.get("avg_power"),
        summary.get("max_power"),
        summary.get("avg_hr"),
        summary.get("max_hr"),
        summary.get("avg_cadence"),
        summary.get("max_cadence"),
        summary.get("distance_km"),
        summary.get("total_work_kj"),
        str(summary.get("time_in_zones")),
    ))

    conn.commit()
    conn.close()
