import os
import dropbox
import pandas as pd
from fitparse import FitFile
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import io
import numpy as np

load_dotenv()

app = FastAPI()

# Load environment variables
DROPBOX_REFRESH_TOKEN = os.getenv("DROPBOX_REFRESH_TOKEN")
DROPBOX_APP_KEY = os.getenv("DROPBOX_APP_KEY")
DROPBOX_APP_SECRET = os.getenv("DROPBOX_APP_SECRET")
DROPBOX_FOLDER = os.getenv("DROPBOX_FOLDER", "/Apps/WahooFitness")

def get_dropbox_client():
    if not all([DROPBOX_REFRESH_TOKEN, DROPBOX_APP_KEY, DROPBOX_APP_SECRET]):
        raise ValueError("Missing Dropbox environment variables.")
    return dropbox.Dropbox(
        oauth2_refresh_token=DROPBOX_REFRESH_TOKEN,
        app_key=DROPBOX_APP_KEY,
        app_secret=DROPBOX_APP_SECRET
    )

def clean_json_unsafe_values(data):
    def clean(obj):
        if isinstance(obj, float):
            if np.isnan(obj) or np.isinf(obj):
                return None
        return obj
    if isinstance(data, dict):
        return {k: clean(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [clean(v) for v in data]
    return clean(data)

def parse_fit_file(file_content: bytes):
    fitfile = FitFile(io.BytesIO(file_content))
    records = []
    for record in fitfile.get_messages('record'):
        record_data = {}
        for field in record:
            record_data[field.name] = field.value
        records.append(record_data)
    return pd.DataFrame(records)

@app.get("/rides")
def list_rides():
    try:
        dbx = get_dropbox_client()
        res = dbx.files_list_folder(DROPBOX_FOLDER)
        rides = [entry.name for entry in res.entries if isinstance(entry, dropbox.files.FileMetadata)]
        return JSONResponse(content=clean_json_unsafe_values(rides))
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": f"Failed to list Dropbox folder: {str(e)}"})

@app.get("/latest-ride-data")
def latest_ride_data():
    try:
        dbx = get_dropbox_client()
        res = dbx.files_list_folder(DROPBOX_FOLDER)
        files = [entry for entry in res.entries if isinstance(entry, dropbox.files.FileMetadata)]
        if not files:
            return JSONResponse(status_code=404, content={"detail": "No ride files found in Dropbox."})
        latest = sorted(files, key=lambda x: x.client_modified)[-1]
        _, res = dbx.files_download(latest.path_display)
        df = parse_fit_file(res.content)
        return JSONResponse(content=clean_json_unsafe_values(df.to_dict(orient="records")))
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": f"Failed to parse ride data: {str(e)}"})

@app.get("/env-check")
def env_check():
    return {
        "DROPBOX_APP_KEY": DROPBOX_APP_KEY is not None,
        "DROPBOX_APP_SECRET": DROPBOX_APP_SECRET is not None,
        "DROPBOX_REFRESH_TOKEN": DROPBOX_REFRESH_TOKEN is not None,
        "DROPBOX_FOLDER": DROPBOX_FOLDER
    }
