from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import os
import dropbox
from dotenv import load_dotenv
from fitparse import FitFile
from datetime import datetime
import json

load_dotenv()

app = FastAPI()

DROPBOX_TOKEN = os.getenv("DROPBOX_TOKEN")
DROPBOX_FOLDER = os.getenv("DROPBOX_FOLDER") or ""
db = dropbox.Dropbox(DROPBOX_TOKEN)

def sanitize_for_json(data):
    def default(o):
        if isinstance(o, (datetime)):
            return o.isoformat()
        if isinstance(o, float):
            if o == float("inf") or o == float("-inf") or o != o:  # NaN check
                return None
        return str(o)
    return json.loads(json.dumps(data, default=default))

def list_fit_files():
    try:
        res = db.files_list_folder(DROPBOX_FOLDER)
        return [entry.name for entry in res.entries if entry.name.endswith(".fit")]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list Dropbox folder: {e}")

def get_file_bytes(filename):
    path = f"{DROPBOX_FOLDER}/{filename}" if DROPBOX_FOLDER else filename
    try:
        metadata, res = db.files_download(path)
        return res.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to download file: {e}")

def parse_fit_to_seconds(fit_data):
    try:
        fitfile = FitFile(fit_data)
        records = []
        for record in fitfile.get_messages("record"):
            fields = {}
            for field in record:
                fields[field.name] = field.value
            records.append(fields)
        return records
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse FIT file: {e}")

@app.get("/ride/{filename}")
def get_ride_data(filename: str):
    if not filename.endswith(".fit"):
        raise HTTPException(status_code=400, detail="Invalid FIT filename.")

    fit_data = get_file_bytes(filename)
    seconds_data = parse_fit_to_seconds(fit_data)
    return JSONResponse(content=sanitize_for_json(seconds_data))

@app.get("/rides")
def list_rides():
    files = list_fit_files()
    file_infos = []
    for name in files:
        try:
            metadata = db.files_get_metadata(f"{DROPBOX_FOLDER}/{name}" if DROPBOX_FOLDER else name)
            file_infos.append({
                "name": name,
                "server_modified": metadata.server_modified
            })
        except Exception as e:
            file_infos.append({"name": name, "error": str(e)})
    return JSONResponse(content=sanitize_for_json(file_infos))

@app.get("/latest-ride-data")
def get_latest_ride_data():
    files = list_fit_files()
    if not files:
        raise HTTPException(status_code=404, detail="No FIT files found.")

    # Get the latest by server_modified timestamp
    latest_file = None
    latest_time = None
    for name in files:
        try:
            metadata = db.files_get_metadata(f"{DROPBOX_FOLDER}/{name}" if DROPBOX_FOLDER else name)
            if not latest_time or metadata.server_modified > latest_time:
                latest_file = name
                latest_time = metadata.server_modified
        except:
            continue

    if not latest_file:
        raise HTTPException(status_code=500, detail="Unable to determine latest file.")

    fit_data = get_file_bytes(latest_file)
    parsed_data = parse_fit_to_seconds(fit_data)
    return JSONResponse(content=sanitize_for_json(parsed_data))
