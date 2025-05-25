import logging
from scripts.fetch_fit_from_dropbox import get_latest_fit_file_from_dropbox
from scripts.fit_parser import parse_fit_file
from scripts.fit_metrics import calculate_ride_metrics
from scripts.ride_database import store_ride

def process_latest_fit_file(access_token):
    try:
        # 🔧 FIXED: Expect 3 values now
        file_bytes, filename, metadata = get_latest_fit_file_from_dropbox(access_token)
        logging.info(f"Downloaded {filename} from Dropbox")

        fit_df = parse_fit_file(file_bytes)
        summary = calculate_ride_metrics(fit_df)

        ride_id = summary["ride_id"]
        store_ride(ride_id, summary, fit_df.to_dict(orient="records"))

        return summary, fit_df.to_dict(orient="records")
    
    except Exception as e:
        logging.error("Failed to process latest ride", exc_info=True)
        raise RuntimeError(f"Failed to process latest ride: {str(e)}")
