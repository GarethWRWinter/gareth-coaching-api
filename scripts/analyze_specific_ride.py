import pandas as pd
from pathlib import Path

# === Path to the specific CSV you want to inspect
ride_path = Path(__file__).resolve().parents[1] / "data" / "2025-04-26-075434-ELEMNT BOLT 5F01-228-0.csv"

print(f"📂 Analyzing: {ride_path.name}")

# === Load the CSV
df = pd.read_csv(ride_path)

# === Print all available columns
print("\n📊 Columns:")
print(df.columns.tolist())

# === Show total datapoints
print(f"\n🔢 {len(df)} data points\n")

# === Preview first 10 rows
print(df.head(10))
