import os
import dropbox
from fitparse import FitFile
from datetime import datetime
from scripts.ride_database import save_ride_summary
from scripts.sanitize import sanitize_fit_data  # ✅ Correct import
from scripts.fit_metrics import calculate_ride_metrics  # ✅ Exists

def process_latest_fit_file(access_token: str):
    dbx = dropbox.Dropbox(access_token)
    folder_path = os.getenv("DROPBOX_FOLDER", "/WahooFitness")

    # 🔍 Find latest .FIT file in Dropbox
    files = dbx.files_list_folder(folder_path).entries
    fit_files = [f for f in files if f.name.endswith(".fit")]
    if not fit_files:
        raise Exception("No .FIT files found in Dropbox folder")

    latest_file = sorted(fit_files, key=lambda x: x.client_modified, reverse=True)[0]
    file_path = f"{folder_path}/{latest_file.name}"
    metadata, res = dbx.files_download(file_path)
    local_path = f"/tmp/{latest_file.name}"

    with open(local_path, "wb") as f:
        f.write(res.content)

    # 🔄 Parse + sanitize FIT data
    fitfile = FitFile(local_path)
    fitfile.parse()
    sanitized = sanitize_fit_data(fitfile)

    # 📊 Compute ride summary
    summary = calculate_ride_metrics(sanitized)
    summary["ride_id"] = int(datetime.now().timestamp())  # TEMP fallback ride_id
    summary["timestamp"] = datetime.now().isoformat()  # TEMP fallback timestamp

    # 💾 Store summary in SQLite
    save_ride_summary(summary)

    return {
        "ride_id": summary["ride_id"],
        "timestamp": summary["timestamp"],
        "summary": summary,
        "data": sanitized
    }
