import sqlite3
import os
import json
from typing import Any, Dict, List

DB_PATH = os.getenv("DB_PATH", "ride_data.db")

def initialize_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rides (
            ride_id TEXT PRIMARY KEY,
            summary TEXT NOT NULL,
            full_data TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()
    print("✅ ride_database initialized")

def store_ride(ride_id: str, summary: Dict[str, Any], full_data: List[Dict[str, Any]]):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO rides (ride_id, summary, full_data)
        VALUES (?, ?, ?)
    """, (ride_id, json.dumps(summary), json.dumps(full_data)))
    conn.commit()
    conn.close()

def ride_exists(ride_id: str) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM rides WHERE ride_id = ?", (ride_id,))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists

def load_ride_by_id(ride_id: str) -> Dict[str, Any]:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT summary, full_data FROM rides WHERE ride_id = ?", (ride_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        summary = json.loads(row[0])
        full_data = json.loads(row[1])
        return {"summary": summary, "full_data": full_data}
    return {}

def load_all_rides() -> List[Dict[str, Any]]:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT summary FROM rides")
    rows = cursor.fetchall()
    conn.close()
    return [json.loads(row[0]) for row in rows]
