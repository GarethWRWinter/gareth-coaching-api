import json
import sqlite3
from scripts.sanitize import sanitize

def store_ride(ride_id, summary, seconds):
    conn = sqlite3.connect("ride_data.db")
    c = conn.cursor()

    # Sanitize all values before json.dumps
    summary_clean = sanitize(summary)
    seconds_clean = sanitize(seconds)

    c.execute('''
        CREATE TABLE IF NOT EXISTS rides (
            ride_id TEXT PRIMARY KEY,
            summary TEXT,
            seconds TEXT
        )
    ''')
    c.execute('''
        INSERT OR REPLACE INTO rides (ride_id, summary, seconds)
        VALUES (?, ?, ?)
    ''', (ride_id, json.dumps(summary_clean), json.dumps(seconds_clean)))
    
    conn.commit()
    conn.close()
