# scripts/dropbox_utils.py

import os
import dropbox
from dropbox.exceptions import AuthError
from dotenv import load_dotenv

load_dotenv()

DROPBOX_FOLDER = os.getenv("DROPBOX_FOLDER", "/Apps/WahooFitness")

def get_latest_fit_file_path(access_token: str) -> str:
    """Return the path to the most recent .fit file in the Dropbox folder."""
    dbx = dropbox.Dropbox(access_token)
    try:
        result = dbx.files_list_folder(DROPBOX_FOLDER)
        files = [entry for entry in result.entries if entry.name.endswith(".fit")]

        while result.has_more:
            result = dbx.files_list_folder_continue(result.cursor)
            files.extend([entry for entry in result.entries if entry.name.endswith(".fit")])

        if not files:
            raise FileNotFoundError("No .fit files found in Dropbox folder.")

        files.sort(key=lambda x: x.client_modified, reverse=True)
        return files[0].path_lower
    except AuthError as e:
        raise Exception(f"Dropbox authentication error: {e}")
    except Exception as e:
        raise Exception(f"Error fetching latest .fit file: {e}")

def list_fit_files_in_folder(access_token: str):
    """List all .fit files in the Dropbox folder."""
    dbx = dropbox.Dropbox(access_token)
    try:
        response = dbx.files_list_folder(DROPBOX_FOLDER)
        files = [entry.path_lower for entry in response.entries if entry.name.endswith(".fit")]
        while response.has_more:
            response = dbx.files_list_folder_continue(response_
