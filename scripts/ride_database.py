import sqlite3
import json

DB_NAME = "ride_data.db"

def initialize_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS rides (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        distance REAL,
        avg_power REAL,
        avg_hr REAL,
        tss REAL,
        duration REAL,
        zones TEXT
    )
    """)
    conn.commit()
    conn.close()

def save_ride_summary(summary: dict):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO rides (
        timestamp,
        distance,
        avg_power,
        avg_hr,
        tss,
        duration,
        zones
    ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        summary.get("timestamp"),
        summary.get("distance"),
        summary.get("avg_power"),
        summary.get("avg_hr"),
        summary.get("tss"),
        summary.get("duration"),
        json.dumps(summary.get("zones"))
    ))
    conn.commit()
    conn.close()

def fetch_ride_history():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM rides ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows
