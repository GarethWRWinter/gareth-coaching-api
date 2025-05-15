import os
from scripts.fetch_fit_from_dropbox import get_latest_fit_file_from_dropbox
from scripts.parse_fit import parse_fit_file
from scripts.ride_database import save_ride_summary
from scripts.summary_generator import generate_ride_summary
from models.pydantic_models import RideSummary

def process_latest_fit_file(access_token: str) -> dict:
    local_filename = "latest.fit"

    # Fetch FIT file
    file_data = get_latest_fit_file_from_dropbox(access_token, local_filename)
    with open(local_filename, "wb") as f:
        f.write(file_data["content"])

    # Parse and summarize
    df = parse_fit_file(local_filename)
    summary_dict = generate_ride_summary(df)

    # Validate with Pydantic
    validated_summary = RideSummary(**summary_dict)

    # Save to DB
    save_ride_summary(validated_summary.dict())

    return validated_summary.dict()
