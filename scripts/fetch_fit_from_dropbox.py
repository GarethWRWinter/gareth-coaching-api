import dropbox
import os
from scripts.refresh_token import refresh_access_token

def get_latest_fit_file_from_dropbox() -> dict:
    access_token = refresh_access_token()
    dbx = dropbox.Dropbox(access_token)
    folder_path = os.environ.get("DROPBOX_FOLDER", "")

    res = dbx.files_list_folder(folder_path)
    files = [f for f in res.entries if f.name.endswith(".fit")]

    if not files:
        return {}

    files.sort(key=lambda f: f.client_modified, reverse=True)
    latest_file = files[0]
    metadata, res = dbx.files_download(latest_file.path_lower)

    return {
        "name": latest_file.name,
        "path": latest_file.path_lower,
        "content": res.content
    }
