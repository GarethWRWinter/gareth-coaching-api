import os
from scripts.fetch_and_parse import get_latest_fit_file_from_dropbox
from scripts.ride_database import save_ride_summary, initialize_db
from scripts.summary_generator import generate_summary
from scripts.sanitizer import sanitize_numpy
import dropbox
from dotenv import load_dotenv

load_dotenv()

DROPBOX_TOKEN = os.environ.get("DROPBOX_TOKEN")
DROPBOX_FOLDER = os.environ.get("DROPBOX_FOLDER", "")

def process_latest_fit_file(access_token):
    print("📥 Fetching latest FIT file from Dropbox...")
    data = get_latest_fit_file_from_dropbox(access_token)
    print("✅ FIT file parsed. Generating summary...")

    summary = generate_summary(data)
    print("🧠 Summary generated. Saving to DB...")

    initialize_db()
    save_ride_summary({
        "filename": data["metadata"]["filename"],
        "timestamp": data["metadata"]["timestamp"],
        "duration_s": summary["duration_s"],
        "distance_km": summary["distance_km"],
        "avg_power": summary["avg_power"],
        "avg_heart_rate": summary["avg_heart_rate"],
        "tss": summary["tss"],
        "normalized_power": summary["normalized_power"],
        "time_in_zones": summary["time_in_zones"]
    })

    print("💾 Ride saved to DB.")
    return sanitize_numpy({
        "metadata": data["metadata"],
        "summary": summary
    })
