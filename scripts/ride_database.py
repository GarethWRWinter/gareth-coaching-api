import sqlite3
import json
import os

DB_PATH = "ride_data.db"

def save_ride_summary(summary: dict):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS rides (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            timestamp TEXT,
            duration_s INTEGER,
            avg_power REAL,
            max_power REAL,
            avg_heart_rate REAL,
            max_heart_rate REAL,
            tss REAL,
            time_in_zones TEXT
        )
    ''')
    c.execute('''
        INSERT INTO rides (
            filename, timestamp, duration_s,
            avg_power, max_power,
            avg_heart_rate, max_heart_rate,
            tss, time_in_zones
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        summary["filename"],
        summary["timestamp"],
        summary["duration_s"],
        summary["avg_power"],
        summary["max_power"],
        summary["avg_heart_rate"],
        summary["max_heart_rate"],
        summary["tss"],
        json.dumps(summary["time_in_zones"])
    ))
    conn.commit()
    conn.close()

def fetch_ride_history():
    if not os.path.exists(DB_PATH):
        return []

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM rides ORDER BY timestamp DESC")
    rows = c.fetchall()
    conn.close()

    keys = [
        "id", "filename", "timestamp", "duration_s", "avg_power",
        "max_power", "avg_heart_rate", "max_heart_rate", "tss", "time_in_zones"
    ]

    history = []
    for row in rows:
        ride = dict(zip(keys, row))
        ride["time_in_zones"] = json.loads(ride["time_in_zones"])
        history.append(ride)

    return history
