import pandas as pd
from fitparse import FitFile

def fitfile_to_dataframe(file_path_or_bytes):
    """
    Converts a .FIT file (from a path or raw bytes) to a Pandas DataFrame.
    Returns DataFrame with all valid record fields (timestamp, power, hr, cadence, etc).
    """
    fitfile = FitFile(file_path_or_bytes)

    records = []
    for record in fitfile.get_messages("record"):
        fields = {field.name: field.value for field in record}
        records.append(fields)

    if not records:
        raise ValueError("No records found in the FIT file.")

    df = pd.DataFrame.from_records(records)
    df.dropna(axis=1, how="all", inplace=True)
    return df
