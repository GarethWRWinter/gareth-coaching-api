import os
import dropbox
from scripts.dropbox_auth import refresh_dropbox_token

def fetch_latest_fit_file():
    # Always refresh token first to ensure access token is valid
    refresh_dropbox_token()

    access_token = os.environ.get('DROPBOX_TOKEN')
    folder_path = os.environ.get('DROPBOX_FOLDER', '/Apps/WahooFitness')

    dbx = dropbox.Dropbox(oauth2_access_token=access_token)

    entries = dbx.files_list_folder(folder_path).entries
    latest_file = max(entries, key=lambda entry: entry.client_modified)

    file_name = latest_file.name
    local_path = os.path.join('fit_files', file_name)

    metadata, res = dbx.files_download(latest_file.path_lower)
    with open(local_path, 'wb') as f:
        f.write(res.content)

    return local_path, file_name
