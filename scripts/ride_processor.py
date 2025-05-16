import os
from dotenv import load_dotenv
from scripts.dropbox_utils import get_latest_fit_file_metadata, download_file
from scripts.fit_parser import parse_fit_file
from scripts.fit_sanitizer import sanitize_fit_data
from scripts.fit_metrics import calculate_ride_metrics
from scripts.ride_database import save_ride_summary

load_dotenv()

def process_latest_fit_file(access_token: str) -> dict:
    try:
        # 🧠 Step 1: Get latest file metadata
        latest_file = get_latest_fit_file_metadata(access_token)
        if not latest_file:
            return {"error": "No .fit file found."}

        file_name = latest_file["name"]

        # 💾 Step 2: Download to local temp
        local_path = f"/tmp/{file_name}"
        download_file(access_token, latest_file["path_display"], local_path)

        # 📊 Step 3: Parse + sanitize
        df = parse_fit_file(local_path)
        sanitized = sanitize_fit_data(df)

        # 🔍 Step 4: Calculate metrics
        summary = calculate_ride_metrics(sanitized)

        # 💾 Step 5: Save to SQLite
        save_ride_summary(summary)

        return summary

    except Exception as e:
        return {"error": str(e)}
