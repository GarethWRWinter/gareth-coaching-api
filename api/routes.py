from fastapi import APIRouter
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import os
import dropbox
from fitparse import FitFile
import io

load_dotenv()

router = APIRouter()

@router.get("/latest-ride-data")
def fetch_latest_ride():
    DROPBOX_TOKEN = os.getenv("DROPBOX_TOKEN")
    DROPBOX_FOLDER = os.getenv("DROPBOX_FOLDER", "/Apps/WahooFitness")

    if not DROPBOX_TOKEN:
        return JSONResponse(status_code=500, content={"error": "Missing Dropbox token"})

    dbx = dropbox.Dropbox(DROPBOX_TOKEN)

    try:
        entries = dbx.files_list_folder(DROPBOX_FOLDER).entries
        fit_files = [f for f in entries if f.name.endswith(".fit")]
        if not fit_files:
            return JSONResponse(status_code=404, content={"error": "No .fit files found"})

        latest_file = max(fit_files, key=lambda f: f.client_modified)
        metadata, res = dbx.files_download(f"{DROPBOX_FOLDER}/{latest_file.name}")
        fitfile = FitFile(io.BytesIO(res.content))

        records = []
        for record in fitfile.get_messages("record"):
            data = {field.name: field.value for field in record}
            records.append(data)

        return {"filename": latest_file.name, "records": records[:5]}  # Return first 5 records for brevity

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
