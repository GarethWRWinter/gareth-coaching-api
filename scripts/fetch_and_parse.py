import os
import dropbox
from io import BytesIO
from dotenv import load_dotenv
from scripts.dropbox_auth import refresh_dropbox_token
from scripts.parse_fit import parse_fit_file
from scripts.fit_metrics import calculate_ride_metrics
from scripts.sanitize import sanitize

load_dotenv()

DROPBOX_FOLDER = os.getenv("DROPBOX_FOLDER", "/Apps/WahooFitness")

def get_latest_fit_file_from_dropbox():
    access_token = refresh_dropbox_token()
    dbx = dropbox.Dropbox(access_token)

    response = dbx.files_list_folder(DROPBOX_FOLDER)
    files = [entry for entry in response.entries if isinstance(entry, dropbox.files.FileMetadata)]
    latest_file = max(files, key=lambda x: x.client_modified)
    metadata, res = dbx.files_download(latest_file.path_lower)

    return BytesIO(res.content)

def process_latest_fit_file():
    fit_stream = get_latest_fit_file_from_dropbox()
    fit_bytes = fit_stream.read()
    df = parse_fit_file(fit_bytes)
    summary = calculate_ride_metrics(df)

    summary["full_data"] = df.to_dict(orient="records")  # ✅ attach full second-by-second data

    return sanitize(summary), sanitize(summary["full_data"])
