import fitparse
import pandas as pd
from datetime import datetime
from scripts.ride_database import get_dynamic_ftp

def parse_fit_file(file_path: str):
    """
    Parses a .FIT file and returns a DataFrame with key metrics.
    """
    fitfile = fitparse.FitFile(file_path)
    data = []

    # Dynamically pull FTP from database for proper zone calculation
    ftp = get_dynamic_ftp()

    for record in fitfile.get_messages('record'):
        record_data = {}
        for field in record:
            record_data[field.name] = field.value
        data.append(record_data)

    df = pd.DataFrame(data)

    # Post-processing
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    if 'power' in df.columns:
        df['power'] = df['power'].fillna(0)

    # Example: Adjust power based on FTP if needed
    # (future enhancement, currently we just parse raw)

    return df
