import sqlite3
import json
import os

DB_PATH = "ride_data.db"

def initialize_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rides (
            ride_id TEXT PRIMARY KEY,
            timestamp TEXT,
            duration INTEGER,
            distance REAL,
            avg_power REAL,
            avg_heart_rate REAL,
            avg_cadence REAL,
            normalized_power REAL,
            intensity_factor REAL,
            training_stress_score REAL,
            total_work REAL,
            ftp INTEGER,
            time_in_zones TEXT,
            full_data TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_ride_summary(summary):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO rides (
            ride_id, timestamp, duration, distance, avg_power, avg_heart_rate,
            avg_cadence, normalized_power, intensity_factor,
            training_stress_score, total_work, ftp, time_in_zones, full_data
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        summary["ride_id"],
        summary["timestamp"],
        summary["duration"],
        summary["distance"],
        summary["avg_power"],
        summary["avg_heart_rate"],
        summary["avg_cadence"],
        summary["normalized_power"],
        summary["intensity_factor"],
        summary["training_stress_score"],
        summary["total_work"],
        summary["ftp"],
        json.dumps(summary["time_in_zones"]),
        json.dumps(summary["full_data"])
    ))
    conn.commit()
    conn.close()

def get_all_rides():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT ride_id, timestamp, duration, avg_power, training_stress_score FROM rides ORDER BY timestamp DESC")
    rides = cursor.fetchall()
    conn.close()
    return [
        {
            "ride_id": row[0],
            "timestamp": row[1],
            "duration": row[2],
            "avg_power": row[3],
            "training_stress_score": row[4]
        }
        for row in rides
    ]

def get_ride_by_id(ride_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM rides WHERE ride_id = ?", (ride_id,))
        row = cursor.fetchone()
        if row is None:
            return None
        column_names = [desc[0] for desc in cursor.description]
        ride_dict = dict(zip(column_names, row))
        for key in ["time_in_zones", "full_data"]:
            if key in ride_dict and ride_dict[key]:
                ride_dict[key] = json.loads(ride_dict[key])
        return ride_dict
    finally:
        conn.close()
