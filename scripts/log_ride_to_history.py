import pandas as pd
from pathlib import Path
from datetime import datetime

# === Load latest parsed ride ===
DATA_FOLDER = Path(__file__).resolve().parents[1] / "data"
ride_csv = DATA_FOLDER / "parsed_full_metrics.csv"
df = pd.read_csv(ride_csv)

# === Configuration ===
FTP = 280
history_file = DATA_FOLDER / "ride_history.csv"

# === Extract Ride Date from Timestamp ===
df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
ride_date = df['timestamp'].min().date() if not df['timestamp'].isna().all() else datetime.today().date()

# === Compute NP, IF, TSS ===
df['power'] = pd.to_numeric(df['power'], errors='coerce')
df = df.dropna(subset=['power'])

rolling_power = df['power'].rolling(window=30, min_periods=30).mean() ** 4
np_value = rolling_power.mean() ** 0.25 if not rolling_power.empty else 0
if_value = np_value / FTP
tss = (len(df) / 60 * np_value * if_value) / (FTP * 60) * 100

# === Power Zones
df['power_ratio'] = df['power'] / FTP
zone_seconds = {}
zones = {
    "Z1": (0, 0.55),
    "Z2": (0.56, 0.75),
    "Z3": (0.76, 0.90),
    "Z4": (0.91, 1.05),
    "Z5": (1.06, 1.20),
    "Z6": (1.21, 1.50),
    "Z7": (1.51, float('inf')),
}
for zone, (low, high) in zones.items():
    zone_seconds[zone] = df[(df['power_ratio'] >= low) & (df['power_ratio'] <= high)].shape[0]

# === Build entry
entry = {
    "date": ride_date,
    "filename": ride_csv.name,
    "NP": round(np_value),
    "IF": round(if_value, 2),
    "TSS": round(tss, 1),
    **zone_seconds
}

# === Save or Append to ride_history.csv
if history_file.exists():
    history_df = pd.read_csv(history_file)
    if ride_csv.name in history_df["filename"].values:
        print(f"⚠️ Ride already logged: {ride_csv.name}")
    else:
        history_df = pd.concat([history_df, pd.DataFrame([entry])], ignore_index=True)
        history_df.to_csv(history_file, index=False)
        print(f"✅ Logged new ride: {ride_csv.name}")
else:
    pd.DataFrame([entry]).to_csv(history_file, index=False)
    print(f"✅ Created new ride history log.")
