import pandas as pd
from fitparse import FitFile

def parse_fit_file(file_path: str):
    fitfile = FitFile(file_path)
    records = []

    for record in fitfile.get_messages("record"):
        record_data = {field.name: field.value for field in record}
        records.append(record_data)

    df = pd.DataFrame(records)
    df = df.dropna(subset=['timestamp'])
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['power'] = df['power'].fillna(0)
    df['heart_rate'] = df['heart_rate'].fillna(0)
    return df
