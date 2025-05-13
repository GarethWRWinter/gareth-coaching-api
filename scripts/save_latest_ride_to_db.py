import os
import dropbox
import pandas as pd
from fitparse import FitFile
from scripts.ride_database import save_ride_summary
from scripts.sanitize import sanitize_dict
from scripts.refresh_token import get_dropbox_access_token
from io import BytesIO

DROPBOX_FOLDER = os.getenv("DROPBOX_FOLDER", "/Apps/WahooFitness")

def process_latest_fit_file(access_token: str):
    print("Starting process_latest_fit_file()")

    # Set up Dropbox client
    dbx = dropbox.Dropbox(oauth2_access_token=access_token)

    # List files in the Dropbox folder
    try:
        result = dbx.files_list_folder(DROPBOX_FOLDER)
        latest_file = sorted(result.entries, key=lambda x: x.client_modified, reverse=True)[0]
    except Exception as e:
        raise RuntimeError(f"Failed to list folder or get latest file: {e}")

    dbx_path = latest_file.path_lower
    print(f"Downloading latest file: {dbx_path}")

    # Download the file
    metadata, res = dbx.files_download(dbx_path)
    fit_data = res.content

    # Parse the FIT file
    fitfile = FitFile(BytesIO(fit_data))
    records = []

    for record in fitfile.get_messages("record"):
        row = {}
        for field in record:
            row[field.name] = field.value
        records.append(row)

    df = pd.DataFrame(records)
    df.dropna(how="all", inplace=True)

    # Sanitize all fields
    json_data = sanitize_dict(df.to_dict(orient="list"))

    # Save summary to DB
    save_ride_summary(json_data)

    print("✅ FIT file processed and saved")
    return json_data
