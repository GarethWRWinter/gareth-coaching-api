import sqlite3
import json
from pathlib import Path
import pandas as pd
from scripts.sanitize import sanitize

# ✅ Path to persistent SQLite database file
DB_PATH = Path("ride_data.db")

# ✅ Create the table if it doesn't exist
def initialize_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS rides (
            ride_id TEXT PRIMARY KEY,
            summary TEXT,
            seconds TEXT
        )
    ''')
    conn.commit()
    conn.close()

# ✅ Save ride data to the database
def store_ride(ride_id, summary):
    summary = sanitize(summary)
    seconds = sanitize(summary.get("full_data", []))  # ✅ FIXED KEY

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO rides (ride_id, summary, seconds)
        VALUES (?, ?, ?)
    ''', (ride_id, json.dumps(summary), json.dumps(seconds)))
    conn.commit()
    conn.close()

# ✅ Retrieve all stored ride summaries (with full metadata)
def get_all_rides():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT ride_id, summary FROM rides ORDER BY ride_id DESC")
    rows = cursor.fetchall()
    conn.close()

    rides = []
    for ride_id, summary_json in rows:
        summary = json.loads(summary_json)
        summary["ride_id"] = ride_id
        rides.append(sanitize(summary))
    return rides

# ✅ Retrieve full summary + second-by-second data for a specific ride
def get_ride_by_id(ride_id: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT summary, seconds FROM rides WHERE ride_id = ?", (ride_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        summary = sanitize(json.loads(row[0]))
        seconds = sanitize(json.loads(row[1]))
        return summary, seconds
    return None, None

# ✅ NEW: Get lightweight ride summaries for trend analysis (no second-by-second data)
def get_all_ride_summaries():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT ride_id, summary FROM rides ORDER BY ride_id DESC")
    rows = cursor.fetchall()
    conn.close()

    summaries = []
    for ride_id, summary_json in rows:
        summary = json.loads(summary_json)
        summary["ride_id"] = ride_id
        for key in ["full_data"]:  # remove heavy keys
            summary.pop(key, None)
        summaries.append(sanitize(summary))
    return summaries
