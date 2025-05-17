# scripts/parse_fit_to_df.py

from fitparse import FitFile
import pandas as pd

def parse_fit_to_dataframe(fit_file_path):
    try:
        fitfile = FitFile(fit_file_path)
        records = []

        for record in fitfile.get_messages("record"):
            record_data = {}
            for field in record:
                if field.name and field.value is not None:
                    record_data[field.name] = field.value
            if record_data:
                records.append(record_data)

        # ✅ THIS IS THE CRITICAL LINE
        df = pd.DataFrame(records)
        return df

    except Exception as e:
        print(f"❌ Failed to parse {fit_file_path}: {e}")
        return pd.DataFrame()
