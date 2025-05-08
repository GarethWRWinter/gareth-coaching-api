from fitparse import FitFile
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt

# === Load FIT file ===
fit_file_path = Path(__file__).resolve().parents[1] / "data" / "2025-05-01-064707-ELEMNT BOLT 5F01-229-0.fit"
fitfile = FitFile(str(fit_file_path))

# === Extract all relevant pedal fields ===
records = []
for record in fitfile.get_messages("record"):
    record_data = {}
    for field in record:
        record_data[field.name] = field.value
    records.append(record_data)

df = pd.DataFrame(records)

# === Detect pedal dynamics ===
pedal_fields = [
    "left_right_balance",
    "left_pedal_smoothness", "right_pedal_smoothness",
    "left_torque_effectiveness", "right_torque_effectiveness"
]
available = [f for f in pedal_fields if f in df.columns]

print(f"\n📊 Pedal Dynamics Analyzer for: {fit_file_path.name}\n")
if not available:
    print("❌ No pedal dynamics recorded in this ride.")
    exit()

print(f"✅ Found fields: {', '.join(available)}")

# === Plot available metrics ===
for field in available:
    df[field] = pd.to_numeric(df[field], errors='coerce')
    df[field].dropna(inplace=True)
    if not df[field].empty:
        df[field].plot(title=field, figsize=(10, 4))
        plt.xlabel("Time (record index)")
        plt.ylabel(field.replace("_", " ").title())
        plt.grid(True)
        plt.tight_layout()
        plt.show()
