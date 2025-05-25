from scripts.fetch_fit_from_dropbox import get_latest_fit_file_from_dropbox
from scripts.parse_fit import parse_fit_file
from scripts.fit_metrics import calculate_ride_metrics
from scripts.sanitize import sanitize
import os
from dotenv import load_dotenv

load_dotenv()

def process_latest_fit_file(access_token: str):
    file_bytes, filename, metadata = get_latest_fit_file_from_dropbox(access_token)
    raw_data = parse_fit_file(file_bytes)
    summary = calculate_ride_metrics(raw_data, filename)
    sanitized = sanitize(summary)
    return raw_data, sanitized, metadata
