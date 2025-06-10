# scripts/fetch_and_parse.py
import os
import dropbox
from dropbox.files import FileMetadata
from scripts.dropbox_auth import refresh_dropbox_token

# Fetch the latest .fit file from Dropbox using a refreshed access token
def fetch_latest_fit_file() -> str:
    # Always refresh the access token
    access_token = refresh_dropbox_token()
    dbx = dropbox.Dropbox(access_token)
    
    folder_path = os.getenv("DROPBOX_FOLDER", "/Apps/WahooFitness")
    fit_files = []

    try:
        entries = dbx.files_list_folder(folder_path).entries
        for entry in entries:
            if isinstance(entry, FileMetadata) and entry.name.endswith(".fit"):
                fit_files.append(entry.name)
        fit_files.sort(reverse=True)
        if fit_files:
            return fit_files[0]
        else:
            raise FileNotFoundError("No .fit files found in Dropbox.")
    except Exception as e:
        print(f"Error listing .fit files: {e}")
        raise

# Download the specified .fit file from Dropbox using refreshed token
def download_fit_file(file_name: str, local_path: str) -> None:
    access_token = refresh_dropbox_token()
    dbx = dropbox.Dropbox(access_token)
    folder_path = os.getenv("DROPBOX_FOLDER", "/Apps/WahooFitness")
    dropbox_path = f"{folder_path}/{file_name}"

    try:
        metadata, res = dbx.files_download(path=dropbox_path)
        with open(local_path, "wb") as f:
            f.write(res.content)
    except Exception as e:
        print(f"Error downloading {file_name}: {e}")
        raise
