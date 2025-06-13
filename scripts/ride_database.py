import sqlite3
import json
from typing import List, Dict, Optional
import os

DB_FILE = os.getenv("DB_FILE", "ride_data.db")

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def initialize_database():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rides (
            ride_id TEXT PRIMARY KEY,
            start_time TEXT,
            summary_json TEXT,
            seconds_json TEXT
        )
    """)
    conn.commit()
    conn.close()

def store_ride(ride_id: str, start_time: str, summary: dict, seconds: List[dict]):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "REPLACE INTO rides (ride_id, start_time, summary_json, seconds_json) VALUES (?, ?, ?, ?)",
        (ride_id, start_time, json.dumps(summary), json.dumps(seconds))
    )
    conn.commit()
    conn.close()

def get_ride_summary(ride_id: str) -> Optional[Dict]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT summary_json FROM rides WHERE ride_id = ?", (ride_id,))
    row = cursor.fetchone()
    conn.close()
    return json.loads(row["summary_json"]) if row else None

def get_all_ride_summaries() -> List[Dict]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT ride_id, summary_json FROM rides ORDER BY start_time DESC")
    rows = cursor.fetchall()
    conn.close()
    return [{"ride_id": row["ride_id"], **json.loads(row["summary_json"])} for row in rows]

def get_latest_ride_summary() -> Optional[Dict]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT summary_json FROM rides ORDER BY start_time DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    return json.loads(row["summary_json"]) if row else None

def get_latest_ride_id() -> Optional[str]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT ride_id FROM rides ORDER BY start_time DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    return row["ride_id"] if row else None

def get_full_ride_data(ride_id: str) -> Optional[Dict]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT summary_json, seconds_json FROM rides WHERE ride_id = ?", (ride_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "summary": json.loads(row["summary_json"]),
            "data": json.loads(row["seconds_json"])
        }
    return None

def get_all_rides_with_data() -> List[Dict]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT ride_id, start_time, summary_json, seconds_json FROM rides ORDER BY start_time DESC")
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "ride_id": row["ride_id"],
            "start_time": row["start_time"],
            "summary": json.loads(row["summary_json"]),
            "data": json.loads(row["seconds_json"])
        }
        for row in rows
    ]
