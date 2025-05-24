from fitparse import FitFile
import pandas as pd
import io

def parse_fit_to_df(fit_binary: bytes) -> pd.DataFrame:
    """
    Parses a binary .FIT file into a pandas DataFrame.
    Returns only 'record' messages (second-by-second ride data).
    """
    fitfile = FitFile(io.BytesIO(fit_binary))
    records = []

    for record in fitfile.get_messages("record"):
        row = {}
        for field in record:
            row[field.name] = field.value
        if row:
            records.append(row)

    df = pd.DataFrame(records)
    return df
