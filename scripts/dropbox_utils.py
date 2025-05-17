# scripts/dropbox_utils.py

import os
import dropbox
from dropbox.exceptions import AuthError
from dotenv import load_dotenv

load_dotenv()

DROPBOX_FOLDER = os.getenv("DROPBOX_FOLDER", "/Apps/WahooFitness")

def list_fit_files_in_folder(access_token: str):
    """List all .fit files in the Dropbox folder."""
    dbx = dropbox.Dropbox(access_token)
    try:
        response = dbx.files_list_folder(DROPBOX_FOLDER)
        files = [entry.path_lower for entry in response.entries if entry.name.endswith(".fit")]
        while response.has_more:
            response = dbx.files_list_folder_continue(response.cursor)
            files.extend([entry.path_lower for entry in response.entries if entry.name.endswith(".fit")])
        return files
    except AuthError as e:
        raise Exception(f"Dropbox Auth Error: {e}")
    except Exception as e:
        raise Exception(f"Dropbox file listing failed: {e}")

def download_file(access_token: str, dropbox_path: str, local_path: str):
    """Download a file from Dropbox to local disk."""
    dbx = dropbox.Dropbox(access_token)
    try:
        with open(local_path, "wb") as f:
            metadata, res = dbx.files_download(path=dropbox_path)
            f.write(res.content)
    except Exception as e:
        raise Exception(f"Dropbox download failed for {dropbox_path}: {e}")
