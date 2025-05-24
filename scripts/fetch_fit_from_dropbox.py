import os
import dropbox
from dotenv import load_dotenv
from scripts.parse_fit import parse_fit_file
from scripts.fit_metrics import calculate_ride_metrics

load_dotenv()

DROPBOX_TOKEN = os.getenv("DROPBOX_TOKEN")
DROPBOX_FOLDER = os.getenv("DROPBOX_FOLDER", "/Apps/WahooFitness")


def download_latest_fit_file(access_token: str) -> bytes:
    dbx = dropbox.Dropbox(access_token)
    res = dbx.files_list_folder(DROPBOX_FOLDER)
    fit_files = [entry for entry in res.entries if entry.name.endswith(".fit")]
    if not fit_files:
        raise FileNotFoundError("No .fit files found in Dropbox folder.")

    latest_file = sorted(fit_files, key=lambda f: f.server_modified, reverse=True)[0]
    metadata, res = dbx.files_download(latest_file.path_lower)
    return res.content


def process_fit_file(access_token: str):
    fit_bytes = download_latest_fit_file(access_token)
    df = parse_fit_file(fit_bytes)
    summary = calculate_ride_metrics(df)
    return df, summary
