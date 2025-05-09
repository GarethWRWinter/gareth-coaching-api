import os
import dropbox
from dropbox.files import FileMetadata
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

DROPBOX_TOKEN = os.environ.get("DROPBOX_TOKEN")
DROPBOX_FOLDER = os.environ.get("DROPBOX_FOLDER", "/")

def create_dropbox_client():
    if not DROPBOX_TOKEN:
        raise Exception("Missing DROPBOX_TOKEN environment variable.")
    return dropbox.Dropbox(DROPBOX_TOKEN)

def get_latest_dropbox_file(folder_path=DROPBOX_FOLDER):
    dbx = create_dropbox_client()
    entries = dbx.files_list_folder(folder_path).entries

    fit_files = [entry for entry in entries if isinstance(entry, FileMetadata) and entry.name.endswith(".fit")]

    if not fit_files:
        raise Exception("No .fit files found in Dropbox folder.")

    latest_file = max(fit_files, key=lambda file: file.server_modified)

    metadata, res = dbx.files_download(latest_file.path_lower)
    file_bytes = res.content

    return type('LatestFile', (), {
        "name": latest_file.name,
        "bytes": file_bytes
    })()
