import os
import pandas as pd
from dropbox import Dropbox
from sqlalchemy import create_engine
from scripts.get_latest_dropbox_file import get_latest_dropbox_file
from scripts.parse_fit_to_df import fitfile_to_dataframe
from dotenv import load_dotenv

load_dotenv()

DROPBOX_FOLDER = os.environ.get("DROPBOX_FOLDER", "")
DATABASE_URL = "sqlite:///ride_data.db"


def save_latest_ride_to_db(access_token: str) -> dict:
    dbx = Dropbox(access_token)
    latest_file = get_latest_dropbox_file(dbx, DROPBOX_FOLDER)
    if not latest_file:
        raise ValueError("No .FIT file found in Dropbox folder.")

    print(f"[INFO] Latest file: {latest_file.name}")
    metadata, res = dbx.files_download(latest_file.path_display)

    with open("temp.fit", "wb") as f:
        f.write(res.content)

    df = fitfile_to_dataframe("temp.fit")
    if df is None or df.empty:
        raise ValueError("Parsed DataFrame is empty or failed to load.")

    print(f"[INFO] Parsed {len(df)} rows of ride data.")

    engine = create_engine(DATABASE_URL)
    df.to_sql("rides", con=engine, if_exists="append", index=False)

    return {
        "message": "Latest ride saved to database.",
        "rows_saved": len(df),
        "filename": latest_file.name
    }
