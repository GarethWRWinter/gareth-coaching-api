# scripts/ride_database.py

import sqlite3
import json
from typing import Any, Dict, List, Optional

DB_PATH = "ride_data.db"


def initialize_database():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rides (
                ride_id TEXT PRIMARY KEY,
                date TEXT,
                summary TEXT,
                data TEXT
            )
        """)
        conn.commit()


def store_ride(ride_id: str, date: str, summary: Dict[str, Any], data: List[Dict[str, Any]]):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO rides (ride_id, date, summary, data)
            VALUES (?, ?, ?, ?)
        """, (
            ride_id,
            date,
            json.dumps(summary),
            json.dumps(data)
        ))
        conn.commit()


def get_ride_history() -> List[Dict[str, Any]]:
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT ride_id, date, summary FROM rides ORDER BY date DESC")
        rows = cursor.fetchall()
        return [
            {
                "ride_id": row[0],
                "date": row[1],
                "summary": json.loads(row[2])
            }
            for row in rows
        ]


def get_ride_by_id(ride_id: str) -> Optional[Dict[str, Any]]:
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT ride_id, date, summary, data FROM rides WHERE ride_id = ?", (ride_id,))
        row = cursor.fetchone()
        if row:
            return {
                "ride_id": row[0],
                "date": row[1],
                "summary": json.loads(row[2]),
                "data": json.loads(row[3])
            }
        return None


def get_all_rides_with_data() -> List[Dict[str, Any]]:
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT ride_id, date, summary, data FROM rides")
        rows = cursor.fetchall()
        return [
            {
                "ride_id": row[0],
                "date": row[1],
                "summary": json.loads(row[2]),
                "data": json.loads(row[3])
            }
            for row in rows
        ]


def update_ftp_value(ride_id: str, new_ftp: int) -> bool:
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT summary FROM rides WHERE ride_id = ?", (ride_id,))
        row = cursor.fetchone()
        if row:
            summary = json.loads(row[0])
            summary["ftp"] = new_ftp
            cursor.execute("UPDATE rides SET summary = ? WHERE ride_id = ?", (json.dumps(summary), ride_id))
            conn.commit()
            return True
        return False
