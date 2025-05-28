import pandas as pd
from fitparse import FitFile


def parse_fit_file_to_dataframe(file_path: str) -> pd.DataFrame:
    """
    Parses a .FIT file and returns a clean DataFrame with key metrics.
    """
    fitfile = FitFile(file_path)
    records = []

    for record in fitfile.get_messages("record"):
        data = {}
        for field in record:
            if field.name and field.value is not None:
                data[field.name] = field.value
        records.append(data)

    if not records:
        raise ValueError("No record messages found in FIT file.")

    df = pd.DataFrame(records)

    # Ensure timestamps are present and sorted
    if "timestamp" not in df.columns:
        raise ValueError("Missing timestamp field in FIT file.")
    df = df[df["timestamp"].notna()].sort_values("timestamp").reset_index(drop=True)

    return df
