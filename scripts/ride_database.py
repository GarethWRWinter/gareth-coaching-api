# scripts/ride_database.py

import sqlite3
import json

DB_FILE = "ride_data.db"

def initialize_database():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS rides (
            ride_id TEXT PRIMARY KEY,
            summary TEXT,
            data TEXT,
            date TEXT,
            ftp INTEGER
        )
    ''')
    conn.commit()
    conn.close()

def store_ride(ride_id, summary, second_by_second):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO rides (ride_id, summary, data, date, ftp)
        VALUES (?, ?, ?, ?, ?)
    ''', (
        ride_id,
        json.dumps(summary),
        json.dumps(second_by_second),
        summary.get("start_time", ""),
        summary.get("ftp", 0)
    ))
    conn.commit()
    conn.close()

def get_all_rides():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT ride_id, summary FROM rides ORDER BY date DESC")
    results = cursor.fetchall()
    conn.close()
    return [(ride_id, json.loads(summary)) for ride_id, summary in results]

def get_all_rides_with_data():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT summary, data FROM rides ORDER BY date DESC")
    results = cursor.fetchall()
    conn.close()
    return [(json.loads(summary), json.loads(data)) for summary, data in results]

def get_ride_by_id(ride_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT summary, data FROM rides WHERE ride_id = ?", (ride_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        summary, data = row
        return json.loads(summary), json.loads(data)
    return None, None

def update_ftp_value(ride_id, new_ftp):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT summary FROM rides WHERE ride_id = ?", (ride_id,))
    row = cursor.fetchone()
    if row:
        summary = json.loads(row[0])
        summary["ftp"] = new_ftp
        cursor.execute(
            "UPDATE rides SET summary = ?, ftp = ? WHERE ride_id = ?",
            (json.dumps(summary), new_ftp, ride_id)
        )
    conn.commit()
    conn.close()

def get_ride_history():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT ride_id, summary FROM rides ORDER BY date DESC")
    results = cursor.fetchall()
    conn.close()
    return [(ride_id, json.loads(summary)) for ride_id, summary in results]
