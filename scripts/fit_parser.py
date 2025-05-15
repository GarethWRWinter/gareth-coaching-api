# scripts/fit_parser.py

from fitparse import FitFile
import pandas as pd

def parse_fit_file(file_data: bytes) -> pd.DataFrame:
    fitfile = FitFile(file_data)
    records = []

    for record in fitfile.get_messages('record'):
        record_data = {}
        for field in record:
            record_data[field.name] = field.value
        records.append(record_data)

    df = pd.DataFrame(records)
    return df
