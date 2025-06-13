import pandas as pd
from fitparse import FitFile

def parse_fit(filepath: str) -> pd.DataFrame:
    fitfile = FitFile(filepath)
    records = []

    for record in fitfile.get_messages("record"):
        row = {}
        for field in record:
            row[field.name] = field.value
        records.append(row)

    df = pd.DataFrame(records)
    return df

# ✅ Alias for API stability
parse_fit_file = parse_fit
