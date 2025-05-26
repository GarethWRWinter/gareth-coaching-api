import os
import dropbox
from dotenv import load_dotenv
from scripts.dropbox_auth import refresh_dropbox_token
from scripts.ride_database import get_all_rides
from scripts.ride_processor import process_fit_file

load_dotenv()

DROPBOX_FOLDER = os.getenv("DROPBOX_FOLDER", "/Apps/WahooFitness")

def get_all_fit_files_from_dropbox():
    access_token = refresh_dropbox_token()
    dbx = dropbox.Dropbox(access_token)
    response = dbx.files_list_folder(DROPBOX_FOLDER)

    files = [
        entry for entry in response.entries
        if isinstance(entry, dropbox.files.FileMetadata) and entry.name.endswith(".fit")
    ]
    return sorted(files, key=lambda x: x.client_modified)

def run_backfill():
    existing_rides = {ride["ride_id"] for ride in get_all_rides()}
    files = get_all_fit_files_from_dropbox()

    added = 0
    skipped = 0

    for file in files:
        ride_id = file.name.split(".")[0]
        if ride_id in existing_rides:
            skipped += 1
            continue

        metadata, res = dropbox.Dropbox(refresh_dropbox_token()).files_download(file.path_lower)
        fit_bytes = res.content
        process_fit_file(fit_bytes)
        added += 1

    return {"backfilled": added, "skipped": skipped, "total": added + skipped}

if __name__ == "__main__":
    result = run_backfill()
    print(result)
