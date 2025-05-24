import sqlite3
import json
from scripts.sanitize import sanitize

DB_PATH = "ride_data.db"

def initialize_database():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS rides (
                ride_id TEXT PRIMARY KEY,
                summary_json TEXT
            )
        ''')
        conn.commit()

def store_ride(ride_summary: dict):
    ride_id = ride_summary.get("ride_id")
    if not ride_id:
        raise ValueError("Missing ride_id in ride_summary.")
    summary_json = json.dumps(sanitize(ride_summary))
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "REPLACE INTO rides (ride_id, summary_json) VALUES (?, ?)",
            (ride_id, summary_json)
        )
        conn.commit()

def get_all_ride_summaries():
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute("SELECT summary_json FROM rides").fetchall()
    return [json.loads(row[0]) for row in rows]

def get_ride_by_id(ride_id: str):
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute("SELECT summary_json FROM rides WHERE ride_id = ?", (ride_id,)).fetchone()
    if row:
        return json.loads(row[0])
    else:
        return {"detail": "Not Found"}
