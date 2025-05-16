import os
import tempfile
from datetime import datetime
from scripts.dropbox_utils import get_latest_fit_file_metadata, download_file
from scripts.fit_sanitizer import sanitize_fit_data
from scripts.fit_metrics import calculate_ride_metrics
from scripts.ride_database import save_ride_summary


def process_latest_fit_file(access_token: str):
    # 🧠 Get latest FIT file metadata
    metadata = get_latest_fit_file_metadata(access_token)
    if not metadata:
        return {"error": "No FIT file found in Dropbox."}

    file_name = metadata["name"]
    dropbox_path = metadata["path_display"]

    # 💾 Download to temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".fit") as tmp_file:
        download_file(access_token, dropbox_path, tmp_file.name)
        local_path = tmp_file.name

    # 🔍 Parse + sanitize
    sanitized = sanitize_fit_data(local_path)

    # 📊 Compute metrics
    summary = calculate_ride_metrics(sanitized)

    # 🛡 Skip DB write if parse failed
    if "error" in summary:
        return {
            "error": summary["error"],
            "ride_id": None,
            "timestamp": datetime.now().isoformat()
        }

    # 📌 Add fallback IDs
    summary["ride_id"] = int(datetime.now().timestamp())
    summary["timestamp"] = datetime.now().isoformat()

    # 💾 Save to DB
    save_ride_summary(summary)

    return summary
