from scripts.fetch_fit_from_dropbox import get_latest_fit_file_from_dropbox
from scripts.fit_parser import calculate_ride_metrics
import pandas as pd
import fitparse

def process_latest_fit_file(access_token):
    file_name, local_path = get_latest_fit_file_from_dropbox(access_token)
    if not file_name or not local_path:
        return None

    fitfile = fitparse.FitFile(local_path)
    records = []
    for record in fitfile.get_messages("record"):
        record_data = {}
        for field in record:
            record_data[field.name] = field.value
        records.append(record_data)

    df = pd.DataFrame(records)
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"])

    ftp = 250  # Default FTP
    metrics = calculate_ride_metrics(df, ftp)

    return {
        "file_name": file_name,
        "metrics": metrics,
        "records_count": len(df),
    }
