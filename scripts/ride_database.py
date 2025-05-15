import sqlite3
from models.pydantic_models import RideSummary
import json

DB_PATH = "ride_data.db"

def save_ride_summary(summary: RideSummary):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ride_summaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ride_id TEXT UNIQUE,
            date TEXT,
            duration_sec INTEGER,
            avg_power REAL,
            max_power INTEGER,
            avg_hr REAL,
            max_hr INTEGER,
            avg_cadence REAL,
            max_cadence INTEGER,
            distance_km REAL,
            total_work_kj REAL,
            time_in_zones TEXT,
            full_data_json TEXT
        )
    """)

    cursor.execute("""
        INSERT OR REPLACE INTO ride_summaries (
            ride_id, date, duration_sec, avg_power, max_power,
            avg_hr, max_hr, avg_cadence, max_cadence,
            distance_km, total_work_kj, time_in_zones, full_data_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        summary.ride_id, summary.date, summary.duration_sec, summary.avg_power,
        summary.max_power, summary.avg_hr, summary.max_hr,
        summary.avg_cadence, summary.max_cadence, summary.distance_km,
        summary.total_work_kj, json.dumps(summary.time_in_zones), json.dumps(summary.full_data)
    ))

    conn.commit()
    conn.close()

def get_all_ride_summaries():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT ride_id, date, duration_sec, avg_power, avg_hr, avg_cadence
        FROM ride_summaries ORDER BY date DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "ride_id": r[0],
            "date": r[1],
            "duration_min": round(r[2] / 60),
            "avg_power": r[3],
            "avg_hr": r[4],
            "avg_cadence": r[5]
        }
        for r in rows
    ]

def get_ride_by_id(ride_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT full_data_json FROM ride_summaries WHERE ride_id = ?
    """, (ride_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return json.loads(row[0])
    return None
