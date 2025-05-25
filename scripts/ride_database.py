import os
import sqlite3
import pandas as pd
from datetime import datetime

DATABASE_PATH = "ride_data.db"

def initialize_database():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rides (
            ride_id TEXT PRIMARY KEY,
            start_time TEXT,
            duration INTEGER,
            distance REAL,
            avg_power REAL,
            avg_hr REAL,
            avg_cadence REAL,
            max_power REAL,
            max_hr REAL,
            max_cadence REAL,
            tss REAL,
            ftp INTEGER,
            zone1 INTEGER,
            zone2 INTEGER,
            zone3 INTEGER,
            zone4 INTEGER,
            zone5 INTEGER,
            zone6 INTEGER,
            zone7 INTEGER,
            json_data TEXT
        )
    """)
    conn.commit()
    conn.close()

def store_ride(summary, full_data):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO rides (
            ride_id, start_time, duration, distance, avg_power, avg_hr, avg_cadence,
            max_power, max_hr, max_cadence, tss, ftp,
            zone1, zone2, zone3, zone4, zone5, zone6, zone7, json_data
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        summary["ride_id"],
        summary["start_time"],
        summary["duration"],
        summary["distance"],
        summary["avg_power"],
        summary["avg_hr"],
        summary["avg_cadence"],
        summary["max_power"],
        summary["max_hr"],
        summary["max_cadence"],
        summary["tss"],
        summary["ftp"],
        summary["time_in_zones"]["zone1"],
        summary["time_in_zones"]["zone2"],
        summary["time_in_zones"]["zone3"],
        summary["time_in_zones"]["zone4"],
        summary["time_in_zones"]["zone5"],
        summary["time_in_zones"]["zone6"],
        summary["time_in_zones"]["zone7"],
        full_data.to_json(orient="records")
    ))
    conn.commit()
    conn.close()

def get_all_rides():
    conn = sqlite3.connect(DATABASE_PATH)
    df = pd.read_sql_query("SELECT * FROM rides ORDER BY start_time DESC", conn)
    conn.close()
    return df.to_dict(orient="records")

def get_ride_by_id(ride_id):
    conn = sqlite3.connect(DATABASE_PATH)
    df = pd.read_sql_query("SELECT * FROM rides WHERE ride_id = ?", conn, params=(ride_id,))
    conn.close()
    if df.empty:
        return None
    return df.to_dict(orient="records")[0]

def load_all_rides():
    conn = sqlite3.connect(DATABASE_PATH)
    df = pd.read_sql_query("SELECT * FROM rides ORDER BY start_time ASC", conn)
    conn.close()
    return df.to_dict(orient="records")
