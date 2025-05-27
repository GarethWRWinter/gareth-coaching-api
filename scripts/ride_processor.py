from scripts.fetch_fit_from_dropbox import get_latest_fit_file_from_dropbox
from scripts.fit_parser import parse_fit_file
from scripts.fit_metrics import calculate_ride_metrics
from scripts.ride_database import store_ride, get_all_ride_summaries, get_ride_by_id
from scripts.process_single_fit import process_fit_file

def process_latest_fit_file(access_token: str) -> dict:
    fit_file_path = get_latest_fit_file_from_dropbox(access_token)
    return process_fit_file(fit_file_path)

def backfill_all_rides(access_token: str) -> dict:
    from scripts.fetch_fit_from_dropbox import get_all_fit_files_from_dropbox  # 👈 delayed import to avoid circular ref

    fit_files = get_all_fit_files_from_dropbox(access_token)
    backfilled = 0
    skipped = 0

    for fit_path in fit_files:
        try:
            process_fit_file(fit_path)
            backfilled += 1
        except Exception:
            skipped += 1

    return {"backfilled": backfilled, "skipped": skipped, "total": len(fit_files)}
