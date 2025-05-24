# scripts/fetch_fit_from_dropbox.py

import os
import dropbox
from scripts.dropbox_auth import refresh_dropbox_token

DROPBOX_FOLDER = os.getenv("DROPBOX_FOLDER", "/Apps/WahooFitness")

def get_latest_fit_file_from_dropbox(access_token: str):
    dbx = dropbox.Dropbox(oauth2_access_token=access_token)
    result = dbx.files_list_folder(DROPBOX_FOLDER)
    fit_files = [entry for entry in result.entries if entry.name.endswith('.fit')]

    if not fit_files:
        raise Exception("No .fit files found in Dropbox folder.")

    # Sort by server_modified time (descending)
    fit_files.sort(key=lambda x: x.server_modified, reverse=True)
    latest_file = fit_files[0]

    # Correct usage with dot notation (not subscripting)
    metadata, response = dbx.files_download(latest_file.path_display)
    file_bytes = response.content
    filename = latest_file.name

    return file_bytes, filename
