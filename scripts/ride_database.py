import sqlite3
import json
from datetime import datetime

DB_PATH = "ride_data.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS rides (
            ride_id TEXT PRIMARY KEY,
            filename TEXT,
            date TEXT,
            duration INTEGER,
            distance_km REAL,
            avg_power INTEGER,
            max_power INTEGER,
            time_in_zones TEXT,
            full_data TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_ride_summary(ride_data):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO rides (
                ride_id,
                filename,
                date,
                duration,
                distance_km,
                avg_power,
                max_power,
                time_in_zones,
                full_data
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            ride_data["ride_id"],
            ride_data["filename"],
            ride_data["date"],
            ride_data["duration"],
            ride_data["distance_km"],
            ride_data["avg_power"],
            ride_data["max_power"],
            json.dumps(ride_data.get("time_in_zones", {})),
            json.dumps(ride_data.get("full_data", {}))
        ))
        conn.commit()
    finally:
        conn.close()

def get_all_rides():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT ride_id, filename, date, duration, distance_km, avg_power, max_power FROM rides")
        rows = cursor.fetchall()
        keys = ["ride_id", "filename", "date", "duration", "distance_km", "avg_power", "max_power"]
        return [dict(zip(keys, row)) for row in rows]
    finally:
        conn.close()

def get_ride_by_id(ride_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM rides WHERE ride_id = ?", (ride_id,))
        row = cursor.fetchone()
