from fitparse import FitFile
import pandas as pd

def parse_fit_file_to_dataframe(file_path: str) -> pd.DataFrame:
    """Parse FIT file and return a pandas DataFrame of record data."""
    fitfile = FitFile(file_path)
    records = []

    for record in fitfile.get_messages("record"):
        row = {}
        for field in record:
            row[field.name] = field.value
        if row:
            records.append(row)

    df = pd.DataFrame(records)
    return df
