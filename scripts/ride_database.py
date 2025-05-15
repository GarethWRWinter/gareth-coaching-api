import sqlite3
import json
import os

DB_PATH = "ride_data.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def save_ride_summary(summary):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rides (
            ride_id TEXT PRIMARY KEY,
            date TEXT,
            duration_sec INTEGER,
            avg_power REAL,
            max_power REAL,
            avg_hr REAL,
            max_hr REAL,
            avg_cadence REAL,
            max_cadence REAL,
            distance_km REAL,
            total_work_kj REAL,
            time_in_zones TEXT,
            full_data TEXT
        )
    """)
    cursor.execute("""
        INSERT OR REPLACE INTO rides (
            ride_id, date, duration_sec, avg_power, max_power, avg_hr, max_hr,
            avg_cadence, max_cadence, distance_km, total_work_kj, time_in_zones, full_data
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        summary.ride_id, summary.date, summary.duration_sec, summary.avg_power, summary.max_power,
        summary.avg_hr, summary.max_hr, summary.avg_cadence, summary.max_cadence,
        summary.distance_km, summary.total_work_kj,
        json.dumps(summary.time_in_zones),
        json.dumps(summary.full_data, default=str)
    ))
    conn.commit()
    conn.close()

def get_all_rides():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT ride_id, date, duration_sec, avg_power, max_power FROM rides ORDER BY date")
    rides = cursor.fetchall()
    conn.close()
    return [dict(ride) for ride in rides]

def get_ride_by_id(ride_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM rides WHERE ride_id = ?", (ride_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None
