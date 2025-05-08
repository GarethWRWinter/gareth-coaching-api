# scripts/save_latest_ride_to_db.py

import os
import dropbox
from fitparse import FitFile
import sqlite3
from dotenv import load_dotenv
from dropbox_auth import refresh_dropbox_token

load_dotenv()

def save_latest_ride_to_db():
    # Refresh Dropbox token before doing anything
    refresh_dropbox_token()

    dbx = dropbox.Dropbox(os.environ["DROPBOX_TOKEN"])
    folder_path = os.environ.get("DROPBOX_FOLDER", "/Apps/WahooFitness")

    # Get latest .fit file
    files = dbx.files_list_folder(folder_path).entries
    fit_files = [f for f in files if f.name.endswith(".fit")]
    latest_file = max(fit_files, key=lambda f: f.client_modified)

    _, res = dbx.files_download(latest_file.path_lower)
    fitfile = FitFile(res.content)

    # Parse FIT data
    records = []
    for record in fitfile.get_messages("record"):
        data = {field.name: field.value for field in record}
        records.append(data)

    # Save to DB
    conn = sqlite3.connect("ride_data.db")
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS rides (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            timestamp TEXT,
            data TEXT
        )
    """)

    import json
    c.execute("INSERT INTO rides (filename, timestamp, data) VALUES (?, datetime('now'), ?)",
              (latest_file.name, json.dumps(records)))

    conn.commit()
    conn.close()

    return {
        "filename": latest_file.name,
        "records": records[:5]  # return first 5 for brevity
    }
