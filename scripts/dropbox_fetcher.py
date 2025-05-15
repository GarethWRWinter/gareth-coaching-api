import dropbox
from dotenv import load_dotenv
import os

load_dotenv()

DROPBOX_FOLDER = os.getenv("DROPBOX_FOLDER", "/Apps/WahooFitness")

def get_latest_fit_file_from_dropbox(access_token: str, local_filename: str = "latest.fit") -> bytes:
    dbx = dropbox.Dropbox(oauth2_access_token=access_token)
    try:
        res = dbx.files_list_folder(DROPBOX_FOLDER)
        entries = sorted(
            [f for f in res.entries if f.name.endswith(".fit")],
            key=lambda x: x.client_modified,
            reverse=True
        )
        if not entries:
            raise FileNotFoundError("No .fit file found in Dropbox folder.")
        latest_file_path = entries[0].path_lower
        metadata, res = dbx.files_download(latest_file_path)
        with open(local_filename, "wb") as f:
            f.write(res.content)
        return res.content
    except Exception as e:
        print("❌ Dropbox fetch error:", e)
        return None
