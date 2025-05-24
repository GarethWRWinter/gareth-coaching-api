import io
import pandas as pd
from fitparse import FitFile


def parse_fit_file(fit_bytes: bytes) -> pd.DataFrame:
    fitfile = FitFile(io.BytesIO(fit_bytes))
    records = []

    for record in fitfile.get_messages("record"):
        row = {}
        for field in record:
            row[field.name] = field.value
        if row:
            records.append(row)

    if not records:
        raise ValueError("No records found in FIT file.")

    df = pd.DataFrame(records)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df
