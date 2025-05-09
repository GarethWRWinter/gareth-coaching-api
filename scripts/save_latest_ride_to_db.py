# scripts/save_latest_ride_to_db.py

import os
import dropbox
from fitparse import FitFile
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
from scripts.get_latest_file import get_latest_dropbox_file

load_dotenv()

DROPBOX_FOLDER = os.getenv("DROPBOX_FOLDER", "/Apps/WahooFitness")

def save_latest_ride_to_db(access_token: str):
    dbx = dropbox.Dropbox(access_token)

    # Get latest file from Dropbox
    latest_file = get_latest_dropbox_file(dbx, DROPBOX_FOLDER)

    # Parse the FIT file
    fitfile = FitFile(latest_file.content)
    records = []

    for record in fitfile.get_messages("record"):
        record_data = {}
        for field in record:
            record_data[field.name] = field.value
        records.append(record_data)

    df = pd.DataFrame(records)

    # Save to SQLite
    engine = create_engine("sqlite:///ride_data.db")
    df.to_sql("rides", con=engine, if_exists="append", index=False)

    return {"message": "Latest ride saved to database", "records_saved": len(df)}
