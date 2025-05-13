import os
import dropbox
import pandas as pd
from fitparse import FitFile
from scripts.ride_database import save_ride_summary
from scripts.sanitize import sanitize_dict
from scripts.refresh_token import get_dropbox_access_token

DROPBOX_FOLDER = os.environ.get("DROPBOX_FOLDER", "/Apps/WahooFitness")

def process_latest_fit_file(access_token: str):
    dbx = dropbox.Dropbox(oauth2_access_token=access_token)

    # List folder contents
    files = dbx.files_list_folder(DROPBOX_FOLDER).entries
    fit_files = [f for f in files if isinstance(f, dropbox.files.FileMetadata) and f.name.endswith('.fit')]
    if not fit_files:
        raise ValueError("No .fit files found in Dropbox folder")

    latest_file = sorted(fit_files, key=lambda x: x.server_modified, reverse=True)[0]
    dbx_path = latest_file.path_display  # ✅ FIXED

    metadata, res = dbx.files_download(dbx_path)
    raw_data = res.content

    with open("temp.fit", "wb") as f:
        f.write(raw_data)

    fitfile = FitFile("temp.fit")
    records = []
    for record in fitfile.get_messages("record"):
        record_data = {d.name: d.value for d in record}
        records.append(record_data)

    df = pd.DataFrame(records)
    df = df.dropna(subset=["timestamp", "power"], how="any")

    sanitized = sanitize_dict(df.to_dict(orient="list"))
    save_ride_summary(sanitized)

    return {"status": "Ride saved", "filename": latest_file.name}
