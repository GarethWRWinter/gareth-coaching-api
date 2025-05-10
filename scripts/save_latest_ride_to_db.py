import os
import sqlite3
import datetime
from dropbox import Dropbox
from scripts.get_latest_dropbox_file import get_latest_dropbox_file
from scripts.parse_fit_to_df import fitfile_to_dataframe


DROPBOX_FOLDER = os.environ.get("DROPBOX_FOLDER", "/Apps/WahooFitness")


def create_rides_table_if_missing(conn):
    conn.execute('''
        CREATE TABLE IF NOT EXISTS rides (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            timestamp TEXT,
            duration_seconds INTEGER,
            avg_power REAL,
            avg_heart_rate REAL,
            avg_cadence REAL,
            max_power REAL,
            max_heart_rate REAL,
            max_cadence REAL
        )
    ''')
    conn.commit()


def save_latest_ride_to_db(access_token: str):
    # Step 1: Connect to Dropbox
    dbx = Dropbox(oauth2_access_token=access_token)

    # Step 2: Get latest FIT file
    latest_file_metadata = get_latest_dropbox_file(dbx, DROPBOX_FOLDER)
    file_path = latest_file_metadata.path_display
    file_name = os.path.basename(file_path)
    print(f"[INFO] Latest file: {file_name}")

    # Step 3: Download FIT file to memory
    metadata, res = dbx.files_download(file_path)
    fit_data = res.content

    # Step 4: Parse FIT data into DataFrame
    df = fitfile_to_dataframe(fit_data)
    print(f"[INFO] Parsed {len(df)} rows of ride data.")

    if df.empty:
        raise ValueError("Parsed DataFrame is empty — cannot save ride.")

    # Step 5: Extract ride metrics
    duration_seconds = int((df['timestamp'].iloc[-1] - df['timestamp'].iloc[0]).total_seconds())
    avg_power = df['power'].mean()
    avg_hr = df['heart_rate'].mean()
    avg_cadence = df['cadence'].mean()
    max_power = df['power'].max()
    max_hr = df['heart_rate'].max()
    max_cadence = df['cadence'].max()
    ride_timestamp = df['timestamp'].iloc[0].isoformat()

    # Step 6: Save to SQLite
    conn = sqlite3.connect("ride_data.db")
    create_rides_table_if_missing(conn)

    conn.execute('''
        INSERT INTO rides (
            filename,
            timestamp,
            duration_seconds,
            avg_power,
            avg_heart_rate,
            avg_cadence,
            max_power,
            max_heart_rate,
            max_cadence
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        file_name,
        ride_timestamp,
        duration_seconds,
        avg_power,
        avg_hr,
        avg_cadence,
        max_power,
        max_hr,
        max_cadence
    ))
    conn.commit()
    conn.close()

    return {
        "filename": file_name,
        "timestamp": ride_timestamp,
        "duration_seconds": duration_seconds,
        "avg_power": avg_power,
        "avg_heart_rate": avg_hr,
        "avg_cadence": avg_cadence,
        "max_power": max_power,
        "max_heart_rate": max_hr,
        "max_cadence": max_cadence
    }
