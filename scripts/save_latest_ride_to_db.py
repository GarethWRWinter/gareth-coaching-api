import os
import dropbox
from dotenv import load_dotenv
from scripts.dropbox_auth import refresh_access_token
from scripts.ride_database import save_ride_summary
from scripts.parse_fit import parse_fit_file
from scripts.time_in_zones import calculate_time_in_zones
from scripts.sanitize import sanitize

load_dotenv()

DROPBOX_FOLDER = os.getenv("DROPBOX_FOLDER")
FTP = int(os.getenv("FTP", "308"))

def get_dropbox_client():
    access_token = refresh_access_token()
    return dropbox.Dropbox(oauth2_access_token=access_token)

def get_latest_fit_file_path(dbx):
    entries = dbx.files_list_folder(DROPBOX_FOLDER).entries
    fit_files = [entry for entry in entries if entry.name.endswith(".fit")]
    if not fit_files:
        raise FileNotFoundError("No .FIT files found in Dropbox folder.")
    latest_file = max(fit_files, key=lambda x: x.client_modified)
    return latest_file.path_display

def process_latest_fit_file(access_token: str):
    dbx = dropbox.Dropbox(oauth2_access_token=access_token)
    dbx_path = get_latest_fit_file_path(dbx)
    metadata, res = dbx.files_download(dbx_path)

    data = parse_fit_file(res.content)
    zones = calculate_time_in_zones(data, FTP)

    summary = {
        "filename": os.path.basename(dbx_path),
        "total_seconds": int(data["timestamp"].max() - data["timestamp"].min()),
        "avg_power": int(data["power"].mean()),
        "avg_heart_rate": int(data["heart_rate"].mean()),
        "total_kj": int((data["power"].sum() * 1) / 1000),
        "time_in_zones": zones,
        "ftp": FTP,
    }

    save_ride_summary(data, summary)  # ✅ FIXED LINE
    return sanitize(summary)
