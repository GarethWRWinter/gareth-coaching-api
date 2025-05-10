import os
import dropbox
from datetime import datetime

def get_latest_dropbox_file(access_token: str, folder_path: str):
    print(f"Looking for .FIT files in: {folder_path}")
    dbx = dropbox.Dropbox(access_token)

    try:
        res = dbx.files_list_folder(folder_path)
    except Exception as e:
        print(f"Error accessing Dropbox folder: {e}")
        return None

    fit_files = [
        entry for entry in res.entries
        if entry.name.endswith(".fit") and isinstance(entry, dropbox.files.FileMetadata)
    ]

    if not fit_files:
        print("No .FIT files found.")
        return None

    # Find the latest file by client_modified or server_modified timestamp
    latest_file = max(fit_files, key=lambda f: f.client_modified or f.server_modified)
    print(f"Latest .FIT file found: {latest_file.name} ({latest_file.client_modified})")
    return latest_file
