import os
import dropbox
import sqlite3
import json
from fitparse import FitFile
from dotenv import load_dotenv
from scripts.get_latest_file import get_latest_dropbox_file

load_dotenv()

DROPBOX_TOKEN = os.environ.get("DROPBOX_TOKEN")
DROPBOX_FOLDER = os.environ.get("DROPBOX_FOLDER", "/Apps/WahooFitness")

DB_FILE = "ride_data.db"


def parse_fit_file(file_path):
    fitfile = FitFile(file_path)
    records = []

    for record in fitfile.get_messages("record"):
        record_data = {}
        for field in record:
            record_data[field.name] = field.value
        records.append(record_data)

    return records


def save_latest_ride_to_db(access_token: str):
    dbx = dropbox.Dropbox(oauth2_access_token=access_token)

    latest_file = get_latest_dropbox_file(dbx, DROPBOX_FOLDER)
    if latest_file is None:
        raise ValueError("No .FIT files found in Dropbox.")

    metadata, res = dbx.files_download(latest_file.path_lower)

    # Save temporarily to parse
    temp_filename = "temp_latest_ride.fit"
    with open(temp_filename, "wb") as f:
        f.write(res.content)

    records = parse_fit_file(temp_filename)

    # Create database and table if not exists
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS rides (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            data TEXT
        )
    """
    )

    # Insert ride data
    c.execute(
        "INSERT INTO rides (filename, data) VALUES (?, ?)",
        (latest_file.name, json.dumps(records, default=str)),  # <-- FIXED HERE
    )
    conn.commit()
    conn.close()

    os.remove(temp_filename)

    return {"filename": latest_file.name, "record_count": len(records)}
