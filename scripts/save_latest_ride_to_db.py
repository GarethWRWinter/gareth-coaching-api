import os
from scripts.fetch_fit_from_dropbox import get_latest_fit_file_from_dropbox
from scripts.parse_fit import parse_fit_file
from scripts.ride_database import save_ride_summary
from scripts.summary_generator import generate_ride_summary
from models.pydantic_models import RideSummary

def process_latest_fit_file(access_token: str) -> RideSummary:
    print("✅ [START] process_latest_fit_file")
    local_filename = "latest_ride.fit"

    # Step 1: Download .FIT file from Dropbox
    print("📥 [Step 1] Fetching latest FIT file from Dropbox...")
    file_data = get_latest_fit_file_from_dropbox(access_token, local_filename)
    print("📄 file_data returned:", type(file_data), file_data)

    if not file_data or "content" not in file_data or not file_data["content"]:
        raise ValueError("❌ No FIT file content returned from Dropbox. Check if file exists and token is valid.")

    # Step 2: Save FIT content to disk
    print("💾 [Step 2] Saving file to disk:", local_filename)
    with open(local_filename, "wb") as f:
        f.write(file_data["content"])

    # Step 3: Parse FIT file
    print("🔍 [Step 3] Parsing FIT file...")
    data = parse_fit_file(local_filename)
    print("📊 Parsed FIT data type:", type(data))
    if not data:
        raise ValueError("❌ FIT parsing returned empty data.")

    # Step 4: Generate summary from FIT data
    print("📈 [Step 4] Generating ride summary...")
    summary_dict = generate_ride_summary(data)
    print("🧪 Summary dict keys:", summary_dict.keys())

    # Step 5: Validate with Pydantic
    print("🧱 [Step 5] Validating with RideSummary model...")
    validated_summary = RideSummary(**summary_dict)
    print("✅ RideSummary object created:", validated_summary)

    # Step 6: Save to SQLite
    print("📦 [Step 6] Saving to DB...")
    save_ride_summary(validated_summary)

    print("🏁 [DONE] FIT file processed successfully.")
    return validated_summary
