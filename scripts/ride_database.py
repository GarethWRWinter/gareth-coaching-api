import sqlite3
import json
import os

DB_PATH = os.getenv("RIDE_DB_PATH", "ride_data.db")

def initialize_database():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rides (
                ride_id TEXT PRIMARY KEY,
                summary TEXT,
                seconds TEXT
            )
        ''')
        conn.commit()

def store_ride(ride_id, summary, seconds):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO rides (ride_id, summary, seconds)
            VALUES (?, ?, ?)
        ''', (ride_id, json.dumps(summary), json.dumps(seconds)))
        conn.commit()

def get_all_rides():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT ride_id, summary FROM rides ORDER BY ride_id DESC")
        rows = cursor.fetchall()
        return [
            {
                "ride_id": row[0],
                "summary": json.loads(row[1])
            }
            for row in rows
        ]

def get_ride_by_id(ride_id):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT summary, seconds FROM rides WHERE ride_id = ?", (ride_id,))
        row = cursor.fetchone()
        if row:
            summary = json.loads(row[0])
            seconds = json.loads(row[1])
            return summary, seconds
        return None, None
