import os
import dropbox
import logging

DROPBOX_FOLDER = os.environ.get("DROPBOX_FOLDER", "/WahooFitness")

def get_latest_fit_file_from_dropbox(access_token):
    dbx = dropbox.Dropbox(access_token)
    logging.info("Fetching list of files from Dropbox...")

    res = dbx.files_list_folder(DROPBOX_FOLDER)
    fit_files = [entry for entry in res.entries if entry.name.endswith(".fit")]

    if not fit_files:
        raise FileNotFoundError("No .fit files found in Dropbox folder.")

    latest_file = max(fit_files, key=lambda entry: entry.client_modified)
    metadata, response = dbx.files_download(latest_file.path_display)
    file_bytes = response.content
    filename = latest_file.name

    return file_bytes, filename, metadata  # ✅ 3-tuple required
