import os
import csv
import requests
from pathlib import Path
from fitparse import FitFile
import dropbox

# === CONFIGURATION ===
APP_KEY = "3ge3h3mssudmqzk"
APP_SECRET = "u0bt5xb35zcsrfz"
REFRESH_TOKEN = "Utgw6P4123kAAAAAAAAAAZwtSpLVp7I359i9tlEAqRStjbEJ52hwPQf06EW-ztbl"

DROPBOX_FIT_FOLDER = "/Apps/WahooFitness"
LOCAL_DATA_FOLDER = Path(__file__).resolve().parents[1] / "data"

def get_access_token():
    response = requests.post(
        "https://api.dropboxapi.com/oauth2/token",
        auth=(APP_KEY, APP_SECRET),
        data={
            "grant_type": "refresh_token",
            "refresh_token": REFRESH_TOKEN,
        },
    )
    if response.status_code != 200:
        raise Exception(f"Token refresh failed: {response.text}")
    return response.json()["access_token"]

def parse_fit_to_csv(fit_content, csv_path):
    fitfile = FitFile(fit_content)
    records = []
    all_fieldnames = set()

    for record in fitfile.get_messages("record"):
        record_data = {}
        for field in record:
            record_data[field.name] = str(field.value)
        all_fieldnames.update(record_data.keys())
        records.append(record_data)

    if not records:
        raise Exception("No 'record' messages found in FIT file.")

    with open(csv_path, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=sorted(all_fieldnames))
        writer.writeheader()
        for row in records:
            writer.writerow(row)

def fetch_and_parse_new_fit_files():
    access_token = get_access_token()
    dbx = dropbox.Dropbox(access_token)

    try:
        result = dbx.files_list_folder(DROPBOX_FIT_FOLDER)
    except Exception as e:
        print(f"❌ Error accessing Dropbox folder: {e}")
        return

    for entry in result.entries:
        if not entry.name.endswith(".fit"):
            continue

        filename_stem = Path(entry.name).stem
        fit_path = LOCAL_DATA_FOLDER / entry.name
        csv_path = LOCAL_DATA_FOLDER / f"{filename_stem}.csv"

        print(f"⬇️ Downloading: {entry.name}")
        metadata, res = dbx.files_download(entry.path_display)
        fit_content = res.content

        # ✅ Always save the raw FIT file
        with open(fit_path, "wb") as f:
            f.write(fit_content)
        print(f"📁 Saved raw FIT: {fit_path.name}")

        # Only parse if CSV doesn't already exist
        if csv_path.exists():
            print(f"✅ Already parsed: {entry.name}")
            continue

        try:
            parse_fit_to_csv(fit_content, csv_path)
            print(f"✅ Parsed and saved: {csv_path}")
        except Exception as e:
            print(f"❌ Failed to parse {entry.name}: {e}")

if __name__ == "__main__":
    LOCAL_DATA_FOLDER.mkdir(parents=True, exist_ok=True)
    fetch_and_parse_new_fit_files()
