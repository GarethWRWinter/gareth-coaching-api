import dropbox
import os

def fetch_latest_fit_file():
    dbx = dropbox.Dropbox(os.getenv("DROPBOX_TOKEN"))
    folder_path = os.getenv("DROPBOX_FOLDER", "/WahooFitness")
    entries = dbx.files_list_folder(folder_path).entries
    fit_files = [entry for entry in entries if entry.name.endswith(".fit")]
    latest_fit = sorted(fit_files, key=lambda x: x.server_modified)[-1]

    local_path = f"fit_files_local/{latest_fit.name}"
    with open(local_path, "wb") as f:
        metadata, res = dbx.files_download(latest_fit.path_display)
        f.write(res.content)
    return local_path
