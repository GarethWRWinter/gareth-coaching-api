import pandas as pd
from fitparse import FitFile
from pathlib import Path

# === Config ===
DATA_FOLDER = Path(__file__).resolve().parents[1] / "data"
FILENAME = "2025-05-01-064707-ELEMNT BOLT 5F01-229-0.fit"
fit_file_path = str(DATA_FOLDER / FILENAME)  # Convert to string for FitFile

# === Parse FIT file ===
fitfile = FitFile(fit_file_path)
records = []

for record in fitfile.get_messages("record"):
    row = {}
    for field in record:
        row[field.name] = field.value
    records.append(row)

# === Convert to DataFrame ===
df = pd.DataFrame(records)

# === Show available fields ===
print("\n📊 Available columns:")
print(list(df.columns))
print(f"\n🔢 {len(df)} data points\n")
print(df.head())

# === Save full parsed data ===
out_file = Path(DATA_FOLDER) / "parsed_full_metrics.csv"
df.to_csv(out_file, index=False)
print(f"\n✅ Saved: {out_file.name}")
