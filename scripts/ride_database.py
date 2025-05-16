import sqlite3
import json

DB_PATH = "ride_data.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rides (
            ride_id TEXT PRIMARY KEY,
            filename TEXT,
            date TEXT,
            duration INTEGER,
            distance_km REAL,
            avg_power REAL,
            max_power REAL,
            avg_heart_rate REAL,
            max_heart_rate REAL,
            avg_cadence REAL,
            max_cadence REAL,
            total_work_kj REAL,
            time_in_zones TEXT,
            full_data TEXT
        )
    """)
    conn.commit()
    conn.close()

def get_all_rides():
    init_db()
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
    init_db()
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
