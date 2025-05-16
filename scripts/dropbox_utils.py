import os
import dropbox
from dropbox.files import FileMetadata
from dotenv import load_dotenv

load_dotenv()

DROPBOX_FOLDER = os.getenv("DROPBOX_FOLDER", "/Apps/WahooFitness")

def get_latest_fit_file_path(access_token: str) -> str:
    """Fetch path of the most recent .FIT file in the configured Dropbox folder."""
    dbx = dropbox.Dropbox(access_token)
    response = dbx.files_list_folder(DROPBOX_FOLDER)

    latest_file = None
    latest_time = None

    for entry in response.entries:
        if isinstance(entry, FileMetadata) and entry.name.endswith(".fit"):
            if latest_time is None or entry.server_modified > latest_time:
                latest_file = entry
                latest_time = entry.server_modified

    if latest_file:
        return latest_file.path_lower
    return ""

def download_file(access_token: str, dropbox_path: str, local_path: str) -> None:
    """Download file from Dropbox to local path."""
    dbx = dropbox.Dropbox(access_token)
    with open(local_path, "wb") as f:
        metadata, res = dbx.files_download(path=dropbox_path)
        f.write(res.content)
