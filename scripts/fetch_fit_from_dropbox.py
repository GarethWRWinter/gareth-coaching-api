import os
import dropbox
import logging

from scripts.ride_processor import process_fit_file
from scripts.dropbox_utils import list_fit_files_in_dropbox, download_fit_file_from_dropbox

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


def backfill_ride_history():
    fit_files = list_fit_files_in_dropbox()
    processed = 0
    skipped = 0

    for fit_file in fit_files:
        ride_id = fit_file.replace(".fit", "").replace("/", "_")
        local_path = download_fit_file_from_dropbox(fit_file)

        if local_path:
            try:
                result = process_fit_file(local_path)
                if result:
                    processed += 1
                else:
                    skipped += 1
            except Exception as e:
                print(f"Failed to process {fit_file}: {e}")
                skipped += 1

    return {
        "backfilled": processed,
        "skipped": skipped,
        "total": len(fit_files)
    }
