# scripts/ride_database.py

import sqlite3

DB_FILE = "ride_data.db"

def initialize_database():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rides (
            ride_id TEXT PRIMARY KEY,
            start_time TEXT,
            duration REAL,
            distance REAL,
            tss REAL,
            normalized_power REAL,
            avg_power REAL,
            max_power REAL,
            avg_heart_rate REAL,
            max_heart_rate REAL,
            avg_cadence REAL,
            max_cadence REAL,
            time_in_zones TEXT
        )
    """)
    conn.commit()
    conn.close()


def store_ride(ride_data: dict):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO rides (
            ride_id, start_time, duration, distance, tss,
            normalized_power, avg_power, max_power, avg_heart_rate,
            max_heart_rate, avg_cadence, max_cadence, time_in_zones
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        ride_data["ride_id"],
        ride_data["start_time"],
        ride_data["duration"],
        ride_data["distance"],
        ride_data["tss"],
        ride_data["normalized_power"],
        ride_data["avg_power"],
        ride_data["max_power"],
        ride_data["avg_heart_rate"],
        ride_data["max_heart_rate"],
        ride_data["avg_cadence"],
        ride_data["max_cadence"],
        ride_data["time_in_zones"]
    ))
    conn.commit()
    conn.close()


def get_all_rides():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM rides")
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_ride(ride_id: str):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM rides WHERE ride_id=?", (ride_id,))
    row = cursor.fetchone()
    conn.close()
    return row
