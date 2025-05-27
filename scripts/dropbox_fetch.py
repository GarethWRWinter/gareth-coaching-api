import logging
from scripts.dropbox_utils import list_fit_files_in_dropbox, download_fit_file_from_dropbox

logger = logging.getLogger(__name__)

def get_latest_fit_file_from_dropbox():
    """
    Gets the latest FIT file bytes, filename, and a timestamp identifier.
    """
    files = list_fit_files_in_dropbox()
    if not files:
        raise ValueError("No FIT files found in Dropbox.")

    # Sort and get latest
    latest_file = sorted(files, key=lambda x: x['client_modified'], reverse=True)[0]
    filename = latest_file['name']
    timestamp_str = filename.replace(".fit", "")
    file_bytes = download_fit_file_from_dropbox(filename)

    return file_bytes, filename, timestamp_str
