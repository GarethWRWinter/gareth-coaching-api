import os
from scripts.dropbox_utils import download_fit_file_from_dropbox
from scripts.process_single_fit import process_fit_file

def process_latest_fit_file(access_token, dropbox_path):
    local_path = "/tmp/latest.fit"
    download_fit_file_from_dropbox(access_token, dropbox_path, local_path)
    summary, fit_data = process_fit_file(local_path)
    return summary, fit_data
