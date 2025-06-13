import os
import dropbox

def get_latest_fit_file_from_dropbox(access_token, folder_path):
    dbx = dropbox.Dropbox(access_token)
    try:
        result = dbx.files_list_folder(folder_path)
        fit_files = [entry for entry in result.entries if entry.name.endswith(".fit")]
        if not fit_files:
            raise Exception("No .fit files found in Dropbox folder.")

        latest_file = max(fit_files, key=lambda x: x.client_modified)
        return latest_file.name
    except Exception as e:
        raise Exception(f"Failed to get latest FIT file: {e}")

def download_fit_file_from_dropbox(access_token, folder_path, file_name):
    dbx = dropbox.Dropbox(access_token)
    dropbox_path = f"{folder_path}/{file_name}"
    local_path = f"/tmp/{file_name}"

    try:
        with open(local_path, "wb") as f:
            metadata, res = dbx.files_download(dropbox_path)
            f.write(res.content)
    except Exception as e:
        raise Exception(f"Failed to download FIT file: {e}")

    return local_path
