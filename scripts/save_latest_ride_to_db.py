import os
from scripts.fetch_fit_from_dropbox import get_latest_fit_file_from_dropbox
from scripts.parse_fit import parse_fit_file
from scripts.summary_generator import generate_ride_summary
from scripts.ride_database import save_ride_summary
from models.pydantic_models import RideSummary

def process_latest_fit_file(access_token: str):
    # 1. Download the latest FIT file from Dropbox
    file_data = get_latest_fit_file_from_dropbox(access_token)
    if not file_data or not file_data.get("content") or not file_data.get("filename"):
        raise ValueError("🚫 No FIT file found or failed to download from Dropbox.")

    # 2. Save raw content to disk
    local_filename = file_data["filename"]
    with open(local_filename, "wb") as f:
        f.write(file_data["content"])

    # 3. Parse FIT file into list of dicts
    data = parse_fit_file(local_filename)

    # 4. Generate ride summary
    summary_dict = generate_ride_summary(data)

    # 5. Validate and save
    validated_summary = RideSummary(**summary_dict)
    save_ride_summary(validated_summary)

    return validated_summary.model_dump()
