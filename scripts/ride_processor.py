from scripts.fetch_fit_from_dropbox import get_latest_fit_file_from_dropbox
from scripts.fit_parser import calculate_ride_metrics
import pandas as pd
import fitparse
import sqlite3

def process_latest_fit_file(access_token):
    file_name, local_path = get_latest_fit_file_from_dropbox(access_token)
    if not file_name or not local_path:
        return None

    fitfile = fitparse.FitFile(local_path)
    records = []
    for record in fitfile.get_messages("record"):
        record_data = {}
        for field in record:
            record_data[field.name] = field.value
        records.append(record_data)

    df = pd.DataFrame(records)
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"])

    ftp = 250  # Default FTP
    metrics = calculate_ride_metrics(df, ftp)

    # Save summary to database
    conn = sqlite3.connect("ride_data.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rides (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_name TEXT,
            duration_seconds REAL,
            average_power REAL,
            max_power REAL,
            tss REAL,
            total_seconds_in_zones REAL
        )
    """)
    cursor.execute("""
        INSERT INTO rides (file_name, duration_seconds, average_power, max_power, tss, total_seconds_in_zones)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        file_name,
        metrics["duration_seconds"],
        metrics["average_power"],
        metrics["max_power"],
        metrics["tss"],
        metrics["zones"]["total_seconds"],
    ))
    conn.commit()
    conn.close()

    return {
        "file_name": file_name,
        "metrics": metrics,
        "records_count": len(df),
    }

def get_all_ride_summaries():
    conn = sqlite3.connect("ride_data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM rides ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()

    ride_summaries = []
    for row in rows:
        ride_summary = {
            "id": row[0],
            "file_name": row[1],
            "duration_seconds": row[2],
            "average_power": row[3],
            "max_power": row[4],
            "tss": row[5],
            "total_seconds_in_zones": row[6],
        }
        ride_summaries.append(ride_summary)
    return ride_summaries
