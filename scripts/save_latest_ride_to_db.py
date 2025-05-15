import os
from scripts.fetch_fit_from_dropbox import get_latest_fit_file_from_dropbox
from scripts.parse_fit import parse_fit_file
from scripts.ride_database import save_ride_summary
from scripts.summary_generator import generate_ride_summary
from models.pydantic_models import RideSummary

def process_latest_fit_file(access_token: str) -> dict:
    local_filename = "latest.fit"
    
    # Step 1: Download latest .fit file
    get_latest_fit_file_from_dropbox(access_token, local_filename)

    # Step 2: Parse .fit file to extract second-by-second data
    data = parse_fit_file(local_filename)

    # Step 3: Generate ride summary dictionary
    summary_dict = generate_ride_summary(data)

    # Step 4: Validate with Pydantic model
    validated_summary = RideSummary(**summary_dict)

    # Step 5: Save to SQLite database
    save_ride_summary(validated_summary.dict())

    # Step 6: Return response
    return validated_summary.dict()
