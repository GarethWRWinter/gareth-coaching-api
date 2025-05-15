import os
from scripts.fetch_fit_from_dropbox import get_latest_fit_file_from_dropbox
from scripts.parse_fit import parse_fit_file
from scripts.ride_database import save_ride_summary
from scripts.summary_generator import generate_ride_summary
from models.pydantic_models import RideSummary

def process_latest_fit_file(access_token: str) -> dict:
    local_filename = "latest.fit"
    get_latest_fit_file_from_dropbox(access_token, local_filename)

    data = parse_fit_file(local_filename)
    summary = generate_ride_summary(data)

    save_ride_summary(summary)  # Already sanitized

    # (Optional validation with Pydantic model)
    validated_summary = RideSummary(**summary)
    return validated_summary.dict()
