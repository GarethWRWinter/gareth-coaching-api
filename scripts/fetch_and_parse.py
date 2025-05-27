import os
import dropbox
from dotenv import load_dotenv
from scripts.fit_parser import parse_fit_file

load_dotenv()
DROPBOX_TOKEN = os.getenv("DROPBOX_TOKEN")
DROPBOX_FOLDER = os.getenv("DROPBOX_FOLDER", "/Apps/WahooFitness")

def list_fit_files_in_dropbox():
    dbx = dropbox.Dropbox(DROPBOX_TOKEN)
    response = dbx.files_list_folder(DROPBOX_FOLDER)
    return [entry.name for entry in response.entries if entry.name.endswith(".fit")]

def download_fit_file_from_dropbox(filename: str) -> str:
    dbx = dropbox.Dropbox(DROPBOX_TOKEN)
    dropbox_path = f"{DROPBOX_FOLDER}/{filename}"
    local_path = f"fit_files/{filename}"
    os.makedirs("fit_files", exist_ok=True)

    with open(local_path, "wb") as f:
        metadata, res = dbx.files_download(path=dropbox_path)
        f.write(res.content)

    return local_path

def fetch_and_parse_fit_file(filename: str):
    local_path = download_fit_file_from_dropbox(filename)
    parsed = parse_fit_file(local_path)
    return parsed
