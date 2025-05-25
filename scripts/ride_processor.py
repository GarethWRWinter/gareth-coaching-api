import logging
from scripts.fetch_fit_from_dropbox import get_latest_fit_file_from_dropbox
from scripts.fit_parser import parse_fit_file
from scripts.fit_metrics import calculate_ride_metrics
from scripts.sanitize import sanitize

logger = logging.getLogger(__name__)

def process_latest_fit_file(access_token):
    try:
        # ✅ FIX: Unpack all three values from Dropbox
        file_bytes, filename, metadata = get_latest_fit_file_from_dropbox(access_token)

        # ✅ Parse FIT data
        fit_data = parse_fit_file(file_bytes)

        # ✅ Generate ride summary + metrics
        summary = calculate_ride_metrics(fit_data, filename)

        # ✅ Sanitize before returning
        return sanitize(fit_data), sanitize(summary), filename

    except Exception as e:
        logger.exception("Failed to process latest ride")
        raise RuntimeError(f"Failed to process latest ride: {e}")
