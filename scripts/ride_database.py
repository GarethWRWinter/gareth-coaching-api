import sqlite3
import json
from typing import Dict, List, Optional

DB_PATH = "ride_data.db"

def initialize_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rides (
            ride_id TEXT PRIMARY KEY,
            date TEXT,
            duration REAL,
            tss REAL,
            normalized_power REAL,
            average_power REAL,
            average_heart_rate REAL,
            time_in_zones TEXT,
            second_by_second_data TEXT,
            tags TEXT,
            quality_score REAL,
            ftp INTEGER
        )
    """)
    conn.commit()
    conn.close()

def store_ride(ride: Dict):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO rides (
            ride_id,
            date,
            duration,
            tss,
            normalized_power,
            average_power,
            average_heart_rate,
            time_in_zones,
            second_by_second_data,
            tags,
            quality_score,
            ftp
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        ride["ride_id"],
        ride["date"],
        ride["duration"],
        ride["tss"],
        ride["normalized_power"],
        ride["average_power"],
        ride["average_heart_rate"],
        json.dumps(ride["time_in_zones"]),
        json.dumps(ride["second_by_second_data"]),
        json.dumps(ride.get("tags", [])),
        ride.get("quality_score"),
        ride.get("ftp")
    ))
    conn.commit()
    conn.close()

def get_ride_history() -> List[Dict]:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM rides ORDER BY date DESC")
    rows = cursor.fetchall()
    conn.close()

    columns = [description[0] for description in cursor.description]
    return [dict(zip(columns, row)) for row in rows]

def get_ride_by_id(ride_id: str) -> Optional[Dict]:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM rides WHERE ride_id = ?", (ride_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        columns = [description[0] for description in cursor.description]
        return dict(zip(columns, row))
    return None

def get_all_rides_with_data() -> List[Dict]:
    return get_ride_history()

def update_ftp_value(ride_id: str, ftp: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE rides
        SET ftp = ?
        WHERE ride_id = ?
    """, (ftp, ride_id))
    conn.commit()
    conn.close()
