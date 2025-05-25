import io
import pandas as pd
from fitparse import FitFile

def parse_fit_file(file_bytes):
    """
    Parses a .FIT file from bytes and returns a pandas DataFrame with all relevant records.
    """
    fitfile = FitFile(io.BytesIO(file_bytes))
    records = []

    for record in fitfile.get_messages("record"):
        row = {}
        for field in record:
            row[field.name] = field.value
        if row:
            records.append(row)

    df = pd.DataFrame(records)
    return df
