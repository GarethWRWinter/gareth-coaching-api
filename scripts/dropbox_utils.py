import os
import dropbox
from dotenv import load_dotenv
from scripts.dropbox_auth import refresh_dropbox_token

load_dotenv()

DROPBOX_FOLDER = os.getenv("DROPBOX_FOLDER", "/Apps/WahooFitness")


def get_dropbox_client() -> dropbox.Dropbox:
    """Get a Dropbox client with a refreshed access token."""
    access_token = refresh_dropbox_token()
    return dropbox.Dropbox(oauth2_access_token=access_token)


def list_fit_files():
    """List all .fit files in the configured Dropbox folder."""
    dbx = get_dropbox_client()
    try:
        result = dbx.files_list_folder(DROPBOX_FOLDER)
        return [entry.name for entry in result.entries if entry.name.endswith(".fit")]
    except dropbox.exceptions.ApiError as e:
        raise RuntimeError(f"Failed to list files: {e}")


def download_fit_file(file_name: str, local_path: str = "latest.fit"):
    """Download a .fit file from Dropbox to a local path."""
    dbx = get_dropbox_client()
    dropbox_path = f"{DROPBOX_FOLDER}/{file_name}"
    try:
        with open(local_path, "wb") as f:
            metadata, res = dbx.files_download(path=dropbox_path)
            f.write(res.content)
        return local_path
    except dropbox.exceptions.ApiError as e:
        raise RuntimeError(f"Failed to download file: {e}")
