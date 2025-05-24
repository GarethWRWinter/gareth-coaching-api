# scripts/dropbox_utils.py

import dropbox
from io import BytesIO

def list_fit_files(access_token: str, folder_path: str = "/Apps/WahooFitness") -> list:
    dbx = dropbox.Dropbox(access_token)
    response = dbx.files_list_folder(folder_path)

    # Filter to only .fit files
    fit_files = [
        entry
        for entry in response.entries
        if isinstance(entry, dropbox.files.FileMetadata) and entry.name.endswith(".fit")
    ]
    return fit_files

def download_file_from_dropbox(file_path: str, access_token: str) -> BytesIO:
    dbx = dropbox.Dropbox(access_token)
    metadata, res = dbx.files_download(file_path)
    return BytesIO(res.content)
