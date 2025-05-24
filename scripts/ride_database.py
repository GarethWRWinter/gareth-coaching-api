import sqlite3
import json
import os
import logging
import pandas as pd
import datetime

logger = logging.getLogger(__name__)
DB_PATH = os.getenv("DB_PATH", "ride_data.db")

def initialize_database():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rides (
                ride_id TEXT PRIMARY KEY,
                date TEXT,
                duration_min REAL,
                avg_power INTEGER,
                avg_heart_rate INTEGER,
                tss REAL,
                full_data TEXT
            )
        """)
        conn.commit()
        conn.close()
        logger.info("Database initialized.")
    except Exception as e:
        logger.exception("Failed to initialize database")
        raise

# ✅ Custom encoder to handle datetime/Timestamp
def default_json(obj):
    if isinstance(obj, (datetime.datetime, pd.Timestamp)):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")

def store_ride(summary: dict):
    try:
        initialize_database()

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO rides (
                ride_id,
                date,
                duration_min,
                avg_power,
                avg_heart_rate,
                tss,
                full_data
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            summary["ride_id"],
            summary["start_time"].split(" ")[0],
            summary["duration_min"],
            summary["avg_power"],
            summary["avg_heart_rate"],
            summary["tss"],
            json.dumps(summary, default=default_json)
        ))

        conn.commit()
        conn.close()
        logger.info(f"Stored ride {summary['ride_id']} to DB")

    except Exception as e:
        logger.exception("Failed to store ride in database")
        raise

def get_all_rides():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT ride_id, date, duration_min, avg_power, avg_heart_rate, tss FROM rides")
        rows = cursor.fetchall()
        conn.close()

        return [
            {
                "ride_id": row[0],
                "date": row[1],
                "duration_min": row[2],
                "avg_power": row[3],
                "avg_heart_rate": row[4],
                "tss": row[5]
            }
            for row in rows
        ]
    except Exception as e:
        logger.exception("Error fetching all rides")
        raise

def get_ride_by_id(ride_id: str):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT full_data FROM rides WHERE ride_id = ?", (ride_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        return json.loads(row[0])
    except Exception as e:
        logger.exception(f"Error fetching ride {ride_id}")
        raise

def load_all_rides():
    """✅ For trend analysis: returns all ride summaries as a list of dicts"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT full_data FROM rides")
        rows = cursor.fetchall()
        conn.close()
        return [json.loads(row[0]) for row in rows]
    except Exception as e:
        logger.exception("Failed to load all rides for trend analysis")
        raise
