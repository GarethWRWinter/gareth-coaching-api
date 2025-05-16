# scripts/dropbox_utils.py

import os
import dropbox
from dropbox.files import FileMetadata

def get_latest_fit_file_metadata(access_token: str) -> dict:
    dbx = dropbox.Dropbox(access_token)
    folder = os.getenv("DROPBOX_FOLDER", "/Apps/WahooFitness")

    try:
        entries = dbx.files_list_folder(folder).entries
        fit_files = [f for f in entries if isinstance(f, FileMetadata) and f.name.endswith(".fit")]
        if not fit_files:
            return {}

        latest = max(fit_files, key=lambda f: f.client_modified)
        return {
            "name": latest.name,
            "path_display": latest.path_display,
            "client_modified": latest.client_modified.isoformat()
        }
    except Exception as e:
        return {"error": str(e)}

def download_file(access_token: str, dropbox_path: str, local_path: str):
    dbx = dropbox.Dropbox(access_token)
    try:
        with open(local_path, "wb") as f:
            metadata, res = dbx.files_download(path=dropbox_path)
            f.write(res.content)
    except Exception as e:
        raise RuntimeError(f"Download failed: {e}")
