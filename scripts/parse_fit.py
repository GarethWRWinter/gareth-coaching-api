import io
import pandas as pd
from fitparse import FitFile

def parse_fit_file(fit_content: bytes) -> pd.DataFrame:
    fitfile = FitFile(io.BytesIO(fit_content))
    records = []

    for record in fitfile.get_messages("record"):
        data = {}
        for field in record:
            data[field.name] = field.value
        if data:
            records.append(data)

    df = pd.DataFrame(records)
    df = df.dropna(subset=["timestamp", "power"], how="any")

    # Standardize timestamp column
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["timestamp"] = (df["timestamp"] - df["timestamp"].min()).dt.total_seconds().astype(int)

    return df
