import os
import sqlite3
import json
from scripts.sanitize import sanitize

DB_PATH = os.environ.get("DB_PATH", "ride_data.db")


def initialize_database():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rides (
                ride_id TEXT PRIMARY KEY,
                summary TEXT
            )
        """)
        conn.commit()


def store_ride(ride_summary: dict):
    ride_id = ride_summary.get("ride_id")
    if not ride_id:
        raise ValueError("Missing 'ride_id' in ride summary")

    sanitized_summary = sanitize(ride_summary)

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO rides (ride_id, summary)
            VALUES (?, ?)
        """, (ride_id, json.dumps(sanitized_summary)))
        conn.commit()


def ride_exists(ride_id: str) -> bool:
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM rides WHERE ride_id = ?", (ride_id,))
        return cursor.fetchone() is not None


def get_ride_by_id(ride_id: str) -> dict | None:
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT summary FROM rides WHERE ride_id = ?", (ride_id,))
        result = cursor.fetchone()
        return json.loads(result[0]) if result else None


def get_all_ride_summaries() -> list:
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT summary FROM rides ORDER BY rowid DESC")
        results = cursor.fetchall()
        return [json.loads(row[0]) for row in results]


def load_all_rides() -> list:
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT summary FROM rides")
        results = cursor.fetchall()
        return [json.loads(row[0]) for row in results]
