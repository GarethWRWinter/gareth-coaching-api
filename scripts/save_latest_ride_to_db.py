import os
import dropbox
from fitparse import FitFile
from io import BytesIO
from scripts.ride_database import save_ride_summary
from scripts.sanitize import sanitize_dict
from scripts.refresh_token import get_dropbox_access_token
from dotenv import load_dotenv

load_dotenv()

DROPBOX_FOLDER = os.getenv("DROPBOX_FOLDER", "/Apps/WahooFitness")

def process_latest_fit_file(access_token: str) -> dict:
    dbx = dropbox.Dropbox(oauth2_access_token=access_token)

    # Get all files in the folder
    try:
        res = dbx.files_list_folder(DROPBOX_FOLDER)
    except dropbox.exceptions.ApiError as e:
        raise Exception(f"Failed to list folder: {e}")

    # Find the latest .fit file
    fit_files = [entry for entry in res.entries if entry.name.endswith(".fit")]
    if not fit_files:
        raise Exception("No .fit files found in Dropbox folder.")

    latest_file = sorted(fit_files, key=lambda x: x.server_modified, reverse=True)[0]
    dbx_path = latest_file.path_lower

    # Download the file
    metadata, res = dbx.files_download(dbx_path)
    fitfile = FitFile(BytesIO(res.content))

    records = []
    for record in fitfile.get_messages("record"):
        record_data = {}
        for field in record:
            record_data[field.name] = field.value
        records.append(record_data)

    # Summary
    summary = {
        "filename": latest_file.name,
        "num_records": len(records),
        "duration_seconds": int((records[-1]["timestamp"] - records[0]["timestamp"]).total_seconds()) if records else 0,
        "fields": list(records[0].keys()) if records else [],
    }

    sanitized = sanitize_dict(summary)
    save_ride_summary(latest_file.name, sanitized)

    return sanitized
