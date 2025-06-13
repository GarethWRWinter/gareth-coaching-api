# scripts/fit_parser.py

import os
import pandas as pd
from fitparse import FitFile

def parse_fit_file(file_path):
    fitfile = FitFile(file_path)
    records = []
    metadata = {}

    for record in fitfile.get_messages("record"):
        row = {}
        for record_data in record:
            row[record_data.name] = record_data.value
        records.append(row)

    for message in fitfile.get_messages("session"):
        for data in message:
            metadata[data.name] = data.value

    df = pd.DataFrame(records)

    # Add FTP from environment (fallback to 308)
    ftp = int(os.getenv("FTP", 308))
    metadata["ftp"] = ftp

    return df, metadata
