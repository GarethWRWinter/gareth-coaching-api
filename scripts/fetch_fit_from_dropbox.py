import dropbox
import os

def get_latest_fit_file_from_dropbox(access_token, folder_path=None):
    """
    Fetches the latest .fit file from the given Dropbox folder.
    If folder_path is not provided, it uses the DROPBOX_FOLDER environment variable.
    """
    if folder_path is None:
        folder_path = os.environ.get("DROPBOX_FOLDER", "/Apps/WahooFitness")
    
    dbx = dropbox.Dropbox(access_token)
    
    try:
        res = dbx.files_list_folder(folder_path)
    except dropbox.exceptions.ApiError as e:
        raise Exception(f"Dropbox folder listing failed: {e}")
    
    fit_files = [entry for entry in res.entries if entry.name.endswith(".fit")]
    fit_files.sort(key=lambda x: x.client_modified, reverse=True)

    if fit_files:
        latest_file = fit_files[0]
        local_path = f"/tmp/{latest_file.name}"
        metadata, response = dbx.files_download(path=latest_file.path_display)
        with open(local_path, "wb") as f:
            f.write(response.content)
        return latest_file.name, local_path
    else:
        raise Exception("No .fit files found in Dropbox folder.")
