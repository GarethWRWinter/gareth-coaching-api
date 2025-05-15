import os
import datetime
from uuid import uuid4
from scripts.dropbox_fetcher import get_latest_fit_file_from_dropbox
from scripts.fit_parser import parse_fit_file
from scripts.summary_generator import generate_ride_summary
from scripts.ride_database import save_ride_summary
from models.pydantic_models import RideSummary
from scripts.sanitize import sanitize
import json

def process_latest_fit_file(access_token: str):
    print("✅ [START] process_latest_fit_file")
    print("📥 [Step 1] Fetching latest FIT file from Dropbox...")
    file_data = get_latest_fit_file_from_dropbox(access_token, "latest.fit")
    print("📄 file_data returned:", type(file_data), file_data[:100] if file_data else None)

    if file_data is None:
        raise ValueError("❌ No FIT file content returned from Dropbox. Check if file exists and token is valid.")

    df = parse_fit_file("latest.fit")
    print("📊 [Step 2] Parsed DataFrame:", df.shape)

    summary_dict = generate_ride_summary(df)
    print("📦 [Step 3] Generated summary:", summary_dict.keys())

    # Inject required fields
    summary_dict["ride_id"] = f"{datetime.date.today()}_{uuid4().hex[:6]}"
    summary_dict["full_data"] = json.loads(
        df.astype(object).where(df.notnull(), None).to_json(orient="records")
    )

    validated_summary = RideSummary(**summary_dict)
    save_ride_summary(validated_summary)

    return sanitize(summary_dict)
