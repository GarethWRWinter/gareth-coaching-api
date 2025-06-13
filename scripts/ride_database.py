import sqlite3
from datetime import datetime
import os

DB_PATH = "ride_data.db"


def initialize_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rides (
            ride_id TEXT PRIMARY KEY,
            date TEXT,
            duration REAL,
            avg_power REAL,
            max_power REAL,
            avg_heart_rate REAL,
            max_heart_rate REAL,
            tss REAL,
            normalized_power REAL,
            intensity_factor REAL,
            total_distance REAL,
            total_ascent REAL,
            time_in_zone_1 REAL,
            time_in_zone_2 REAL,
            time_in_zone_3 REAL,
            time_in_zone_4 REAL,
            time_in_zone_5 REAL,
            time_in_zone_6 REAL,
            time_in_zone_7 REAL,
            ftp_used INTEGER
        )
    """)
    conn.commit()
    conn.close()


def store_ride(ride_summary: dict):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO rides (
            ride_id,
            date,
            duration,
            avg_power,
            max_power,
            avg_heart_rate,
            max_heart_rate,
            tss,
            normalized_power,
            intensity_factor,
            total_distance,
            total_ascent,
            time_in_zone_1,
            time_in_zone_2,
            time_in_zone_3,
            time_in_zone_4,
            time_in_zone_5,
            time_in_zone_6,
            time_in_zone_7,
            ftp_used
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        ride_summary.get("ride_id"),
        ride_summary.get("date"),
        ride_summary.get("duration"),
        ride_summary.get("avg_power"),
        ride_summary.get("max_power"),
        ride_summary.get("avg_heart_rate"),
        ride_summary.get("max_heart_rate"),
        ride_summary.get("tss"),
        ride_summary.get("normalized_power"),
        ride_summary.get("intensity_factor"),
        ride_summary.get("total_distance"),
        ride_summary.get("total_ascent"),
        ride_summary.get("time_in_zone_1"),
        ride_summary.get("time_in_zone_2"),
        ride_summary.get("time_in_zone_3"),
        ride_summary.get("time_in_zone_4"),
        ride_summary.get("time_in_zone_5"),
        ride_summary.get("time_in_zone_6"),
        ride_summary.get("time_in_zone_7"),
        ride_summary.get("ftp_used"),
    ))

    conn.commit()
    conn.close()


def fetch_all_rides():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM rides ORDER BY date DESC")
    rows = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    conn.close()

    return [dict(zip(columns, row)) for row in rows]


def fetch_ride_by_id(ride_id: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM rides WHERE ride_id = ?", (ride_id,))
    row = cursor.fetchone()
    columns = [column[0] for column in cursor.description]
    conn.close()

    if row:
        return dict(zip(columns, row))
    else:
        return None


def get_ride_history():
    return fetch_all_rides()


def get_all_rides_with_data():
    return fetch_all_rides()


def update_ftp_value(ride_id: str, new_ftp: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE rides
        SET ftp_used = ?
        WHERE ride_id = ?
    """, (new_ftp, ride_id))
    conn.commit()
    conn.close()
