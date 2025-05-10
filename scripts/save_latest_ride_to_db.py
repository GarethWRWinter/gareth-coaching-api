# scripts/save_latest_ride_to_db.py
import os
import dropbox
from dropbox.files import FileMetadata
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import pandas as pd

from scripts.get_latest_dropbox_file import get_latest_dropbox_file
from scripts.parse_fit_to_df import fitfile_to_dataframe
from scripts.models import Base, Ride

DROPBOX_FOLDER = os.environ.get("DROPBOX_FOLDER", "/Apps/WahooFitness")
DB_PATH = "sqlite:///ride_data.db"

def save_latest_ride_to_db(access_token: str) -> dict:
    dbx = dropbox.Dropbox(oauth2_access_token=access_token)
    latest_file: FileMetadata = get_latest_dropbox_file(dbx, DROPBOX_FOLDER)

    # Download FIT file
    metadata, response = dbx.files_download(latest_file.path_display)
    fit_data = response.content

    # Parse to DataFrame
    df = fitfile_to_dataframe(fit_data)

    # Basic metrics
    timestamp = df["timestamp"].iloc[0]
    duration_seconds = int((df["timestamp"].iloc[-1] - df["timestamp"].iloc[0]).total_seconds())
    avg_power = df["power"].mean()
    max_power = df["power"].max()
    avg_hr = df["heart_rate"].mean()
    max_hr = df["heart_rate"].max()
    tss = (duration_seconds * avg_power) / (3600 * 250) * 100  # crude estimate for now

    # Setup DB
    engine = create_engine(DB_PATH)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    ride = Ride(
        filename=latest_file.name,
        timestamp=timestamp,
        duration_seconds=duration_seconds,
        avg_power=avg_power,
        max_power=max_power,
        avg_heart_rate=avg_hr,
        max_heart_rate=max_hr,
        tss=tss,
    )

    session.add(ride)
    session.commit()
    session.close()

    return {
        "filename": latest_file.name,
        "rows": len(df),
        "timestamp": str(timestamp),
        "duration_s": duration_seconds,
        "avg_power": round(avg_power, 1),
        "max_power": round(max_power, 1),
        "avg_heart_rate": round(avg_hr, 1),
        "max_heart_rate": round(max_hr, 1),
        "tss": round(tss, 1),
    }
