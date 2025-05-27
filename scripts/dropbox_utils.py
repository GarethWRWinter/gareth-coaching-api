import os
import dropbox
import logging

DROPBOX_TOKEN = os.environ.get("DROPBOX_TOKEN")
DROPBOX_FOLDER = os.environ.get("DROPBOX_FOLDER", "/WahooFitness")


def list_fit_files_in_dropbox():
    """Returns a list of all .fit file paths in the configured Dropbox folder."""
    dbx = dropbox.Dropbox(DROPBOX_TOKEN)
    logging.info(f"Listing .fit files from Dropbox folder: {DROPBOX_FOLDER}")

    res = dbx.files_list_folder(DROPBOX_FOLDER)
    fit_files = [entry.path_display for entry in res.entries if entry.name.endswith(".fit")]
    return fit_files


def download_fit_file_from_dropbox(file_path):
    """Downloads a single .fit file and saves it locally in /tmp."""
    dbx = dropbox.Dropbox(DROPBOX_TOKEN)
    local_filename = os.path.join("/tmp", os.path.basename(file_path))

    try:
        metadata, res = dbx.files_download(file_path)
        with open(local_filename, "wb") as f:
            f.write(res.content)
        logging.info(f"Downloaded {file_path} to {local_filename}")
        return local_filename
    except Exception as e:
        logging.error(f"Failed to download {file_path}: {e}")
        return None
