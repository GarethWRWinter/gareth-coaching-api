import sqlite3
import os
import numpy as np

DB_PATH = os.path.join(os.path.dirname(__file__), "../ride_data.db")

def sanitize(obj):
    if isinstance(obj, dict):
        return {k: sanitize(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize(i) for i in obj]
    elif isinstance(obj, np.generic):
        return obj.item()
    return obj

def fetch_ride_history():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM rides ORDER BY timestamp DESC")
    rows = cursor.fetchall()

    col_names = [description[0] for description in cursor.description]
    rides = [dict(zip(col_names, row)) for row in rows]

    conn.close()
    return sanitize(rides)
