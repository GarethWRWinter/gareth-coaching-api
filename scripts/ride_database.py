import sqlite3
from sqlalchemy import create_engine, text

def get_db_connection():
    engine = create_engine("sqlite:///ride_data.db")
    return engine.connect()

def store_ride(ride_summary):
    conn = get_db_connection()
    conn.execute(text("""
        INSERT OR REPLACE INTO rides (
            ride_id, start_time, duration_sec, avg_power, avg_hr, max_power,
            max_hr, tss, normalized_power, left_right_balance, power_zone_times, hr_zone_times
        ) VALUES (
            :ride_id, :start_time, :duration_sec, :avg_power, :avg_hr, :max_power,
            :max_hr, :tss, :normalized_power, :left_right_balance, :power_zone_times, :hr_zone_times
        )
    """), ride_summary)
    conn.close()

def get_dynamic_ftp():
    conn = get_db_connection()
    ftp = conn.execute(text("SELECT ftp FROM athletes LIMIT 1")).fetchone()
    conn.close()
    return ftp[0] if ftp else 250.0
