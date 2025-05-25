import os
from scripts.fetch_fit_from_dropbox import get_latest_fit_file_from_dropbox
from scripts.parse_fit import parse_fit_file
from scripts.fit_metrics import calculate_ride_metrics
from scripts.sanitize import sanitize


def process_latest_fit_file(access_token: str):
    fit_data, filename = get_latest_fit_file_from_dropbox(access_token)  # ✅ fix: unpack tuple
    fit_df, metadata = parse_fit_file(fit_data)
    summary, full_data = calculate_ride_metrics(fit_df, metadata)
    return sanitize(summary), sanitize(full_data)
