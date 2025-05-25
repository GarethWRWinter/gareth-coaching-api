import sqlite3

DB_PATH = "data/ride_data.db"

def initialize_database():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rides (
                ride_id TEXT PRIMARY KEY,
                timestamp TEXT,
                summary_json TEXT,
                full_data_json TEXT
            )
        """)
        conn.commit()

def store_ride(ride_id, timestamp, summary, full_data):
    import json
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO rides (ride_id, timestamp, summary_json, full_data_json)
            VALUES (?, ?, ?, ?)
        """, (
            ride_id,
            timestamp,
            json.dumps(summary),
            json.dumps(full_data)
        ))
        conn.commit()

def get_all_rides():
    import json
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT ride_id, timestamp, summary_json FROM rides ORDER BY timestamp DESC")
        rows = cursor.fetchall()
        return [
            {
                "ride_id": row[0],
                "timestamp": row[1],
                "summary": json.loads(row[2])
            }
            for row in rows
        ]

def get_ride_by_id(ride_id):
    import json
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ride_id, timestamp, summary_json, full_data_json
            FROM rides
            WHERE ride_id = ?
        """, (ride_id,))
        row = cursor.fetchone()
        if row:
            return {
                "ride_id": row[0],
                "timestamp": row[1],
                "summary": json.loads(row[2]),
                "full_data": json.loads(row[3])
            }
        return None
