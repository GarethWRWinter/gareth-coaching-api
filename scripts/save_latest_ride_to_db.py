import os
import dropbox
import tempfile
import pandas as pd
from sqlalchemy import create_engine
from scripts.get_latest_dropbox_file import get_latest_dropbox_file
from scripts.parse_fit_to_dataframe import parse_fit_to_dataframe

DROPBOX_FOLDER = os.environ.get("DROPBOX_FOLDER", "")
DB_FILE = "ride_data.db"

def save_latest_ride_to_db(access_token):
    print("Starting: save_latest_ride_to_db()")
    dbx = dropbox.Dropbox(oauth2_access_token=access_token)
    
    # Get latest file metadata
    latest_file = get_latest_dropbox_file(dbx, DROPBOX_FOLDER)
    if not latest_file:
        raise Exception("No .fit file found in Dropbox folder.")

    file_path = latest_file.path_display
    print(f"Downloading latest .FIT file: {file_path}")
    
    # Download file to temp location
    _, temp_file = tempfile.mkstemp(suffix=".fit")
    with open(temp_file, "wb") as f:
        metadata, res = dbx.files_download(path=file_path)
        f.write(res.content)

    print("Parsing .FIT file to dataframe...")
    df = parse_fit_to_dataframe(temp_file)

    if df.empty:
        raise Exception("Parsed DataFrame is empty. Possible parsing error.")

    print(f"Saving to database: {DB_FILE}")
    engine = create_engine(f"sqlite:///{DB_FILE}")
    df.to_sql("rides", con=engine, if_exists="append", index=False)
    engine.dispose()

    print("Ride saved successfully.")
    return {"message": "Ride saved", "rows": len(df), "file": file_path}
