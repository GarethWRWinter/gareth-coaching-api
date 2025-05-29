import os
import dropbox

def get_latest_fit_file_from_dropbox(access_token):
    dbx = dropbox.Dropbox(access_token)
    folder_path = os.getenv("DROPBOX_FOLDER", "/Apps/WahooFitness")
    files = dbx.files_list_folder(folder_path).entries
    fit_files = [f for f in files if f.name.endswith(".fit")]
    latest = max(fit_files, key=lambda f: f.client_modified)
    return folder_path, latest.name, f"/tmp/{latest.name}"

def download_fit_file_from_dropbox(access_token, folder_path, file_name, local_path):
    dbx = dropbox.Dropbox(access_token)
    metadata, res = dbx.files_download(path=f"{folder_path}/{file_name}")
    with open(local_path, "wb") as f:
        f.write(res.content)
