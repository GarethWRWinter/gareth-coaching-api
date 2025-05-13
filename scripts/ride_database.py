# scripts/ride_database.py

import sqlite3

def save_ride_summary(ride_summary):
    conn = sqlite3.connect("ride_data.db")
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS rides (
            filename TEXT PRIMARY KEY,
            timestamp TEXT,
            duration_s INTEGER,
            avg_power REAL,
            max_power REAL,
            avg_heart_rate REAL,
            max_heart_rate REAL,
            tss REAL,
            zone1_s INTEGER,
            zone2_s INTEGER,
            zone3_s INTEGER,
            zone4_s INTEGER,
            zone5_s INTEGER,
            zone6_s INTEGER
        )
    ''')
    
    c.execute('''
        INSERT OR REPLACE INTO rides VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        ride_summary["filename"],
        ride_summary["timestamp"],
        ride_summary["duration_s"],
        ride_summary["avg_power"],
        ride_summary["max_power"],
        ride_summary["avg_heart_rate"],
        ride_summary["max_heart_rate"],
        ride_summary["tss"],
        ride_summary["time_in_zones"]["zone1_s"],
        ride_summary["time_in_zones"]["zone2_s"],
        ride_summary["time_in_zones"]["zone3_s"],
        ride_summary["time_in_zones"]["zone4_s"],
        ride_summary["time_in_zones"]["zone5_s"],
        ride_summary["time_in_zones"]["zone6_s"]
    ))

    conn.commit()
    conn.close()
