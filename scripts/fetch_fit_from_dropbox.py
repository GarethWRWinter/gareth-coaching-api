import os
from scripts.dropbox_auth import refresh_dropbox_token
from scripts.dropbox_utils import list_fit_files_in_dropbox, download_fit_file_from_dropbox
from scripts.process_single_fit import process_fit_file

def backfill_ride_history():
    access_token = refresh_dropbox_token()
    dropbox_folder = os.environ.get("DROPBOX_FOLDER", "/Apps/WahooFitness")
    filenames = list_fit_files_in_dropbox(access_token, dropbox_folder)

    backfilled, skipped = 0, 0
    for fname in sorted(filenames):
        local_path = os.path.join("/tmp", os.path.basename(fname))
        download_fit_file_from_dropbox(access_token, fname, local_path)
        summary, fit_data = process_fit_file(local_path)
        if summary:
            backfilled += 1
        else:
            skipped += 1

    return {"backfilled": backfilled, "skipped": skipped, "total": len(filenames)}

def get_latest_fit_file_from_dropbox():
    access_token = refresh_dropbox_token()
    dropbox_folder = os.environ.get("DROPBOX_FOLDER", "/Apps/WahooFitness")
    filenames = list_fit_files_in_dropbox(access_token, dropbox_folder)
    if not filenames:
        return None
    return access_token, filenames[-1]
