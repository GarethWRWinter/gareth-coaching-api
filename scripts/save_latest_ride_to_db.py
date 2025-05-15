import os
from scripts.fetch_fit_from_dropbox import get_latest_fit_file_from_dropbox
from scripts.parse_fit import parse_fit_file
from scripts.ride_database import save_ride_summary
from scripts.summary_generator import generate_ride_summary
from models.pydantic_models import RideSummary

def process_latest_fit_file(access_token: str) -> RideSummary:
    print("[Step 1] Access token:", type(access_token))

    local_filename = "latest_ride.fit"

    # Step 2: Download .FIT file
    file_data = get_latest_fit_file_from_dropbox(access_token, local_filename)
    print("[Step 2] FIT file downloaded:", type(file_data))

    if file_data is None or file_data.get("content") is None:
        raise ValueError("No FIT file content returned from Dropbox.")

    # Step 3: Save the file locally
    with open(local_filename, "wb") as f:
        f.write(file_data["content"])

    # Step 4: Parse .FIT into list of dicts
    data = parse_fit_file(local_filename)
    print("[Step 4] Parsed FIT data:", type(data), "Sample:", data[0] if data else "EMPTY")

    # Step 5: Generate summary as dict
    summary_dict = generate_ride_summary(data)
    print("[Step 5] Summary dict:", type(summary_dict), summary_dict)

    # Step 6: Validate with Pydantic
    validated_summary = RideSummary(**summary_dict)
    print("[Step 6] Validated summary:", type(validated_summary))

    # Step 7: Save to DB
    save_ride_summary(validated_summary)
    print("[Step 7] Saved to DB.")

    return validated_summary
