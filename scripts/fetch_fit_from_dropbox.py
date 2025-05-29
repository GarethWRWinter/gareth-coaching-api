import os
import dropbox
from datetime import datetime

DROPBOX_FOLDER = os.getenv("DROPBOX_FOLDER", "/Apps/WahooFitness")
LOCAL_FOLDER = "fit_files_local"

def get_latest_fit_file_from_dropbox(access_token: str):
    dbx = dropbox.Dropbox(access_token)
    
    try:
        res = dbx.files_list_folder(DROPBOX_FOLDER)
        fit_files = [entry for entry in res.entries if entry.name.endswith('.fit')]
        if not fit_files:
            raise FileNotFoundError("No .fit files found in Dropbox folder.")

        # Sort by server_modified time to get the latest
        fit_files.sort(key=lambda x: x.server_modified, reverse=True)
        latest_file = fit_files[0]
        file_name = latest_file.name

        # Ensure local folder exists
        os.makedirs(LOCAL_FOLDER, exist_ok=True)
        local_path = os.path.join(LOCAL_FOLDER, file_name)

        with open(local_path, "wb") as f:
            metadata, res = dbx.files_download(path=latest_file.path_display)
            f.write(res.content)

        return local_path, file_name

    except Exception as e:
        raise RuntimeError(f"Failed to fetch latest FIT file from Dropbox: {e}")
