import sqlite3
import os

DB_PATH = "ride_data.db"

def initialize_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rides (
            ride_id TEXT PRIMARY KEY,
            start_time TEXT,
            end_time TEXT,
            duration_sec INTEGER,
            distance_km REAL,
            avg_power REAL,
            max_power INTEGER,
            avg_heart_rate REAL,
            max_heart_rate INTEGER,
            avg_cadence REAL,
            max_cadence INTEGER,
            total_work REAL,
            tss REAL,
            time_in_zones TEXT
        )
    """)
    conn.commit()
    conn.close()
    print("✅ rides table created or confirmed")

def save_ride_summary(summary):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO rides (
            ride_id, start_time, end_time, duration_sec,
            distance_km, avg_power, max_power,
            avg_heart_rate, max_heart_rate,
            avg_cadence, max_cadence, total_work, tss, time_in_zones
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        summary["ride_id"],
        summary["start_time"],
        summary["end_time"],
        summary["duration_sec"],
        summary["distance_km"],
        summary["avg_power"],
        summary["max_power"],
        summary["avg_heart_rate"],
        summary["max_heart_rate"],
        summary["avg_cadence"],
        summary["max_cadence"],
        summary["total_work"],
        summary["tss"],
        str(summary["time_in_zones"])
    ))
    conn.commit()
    conn.close()

def ride_exists(ride_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM rides WHERE ride_id = ?", (ride_id,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

# 🟢 Run this when file is executed directly
if __name__ == "__main__":
    print("🔧 Initializing database...")
    initialize_db()
