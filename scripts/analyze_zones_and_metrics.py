import pandas as pd
import numpy as np
from pathlib import Path

# === CONFIGURATION ===
FTP = 280  # Set your current Functional Threshold Power (adjust as needed)

# === Load latest ride ===
DATA_FOLDER = Path(__file__).resolve().parents[1] / "data"
latest_csv = sorted(DATA_FOLDER.glob("*.csv"))[-1]
print(f"📂 Analyzing: {latest_csv.name}")

df = pd.read_csv(latest_csv)

# Clean and convert
df['power'] = pd.to_numeric(df['power'], errors='coerce')
df['heart_rate'] = pd.to_numeric(df['heart_rate'], errors='coerce')

df = df.dropna(subset=['power'])  # Drop rows without power

# === Time in Power Zones ===
power_zones = {
    "Z1 Active Recovery": (0, 0.55),
    "Z2 Endurance": (0.56, 0.75),
    "Z3 Tempo": (0.76, 0.90),
    "Z4 Threshold": (0.91, 1.05),
    "Z5 VO2 Max": (1.06, 1.20),
    "Z6 Anaerobic": (1.21, 1.50),
    "Z7 Neuromuscular": (1.51, np.inf)
}

df['power_ratio'] = df['power'] / FTP

zone_counts = {}
for zone, (low, high) in power_zones.items():
    seconds = df[(df['power_ratio'] >= low) & (df['power_ratio'] <= high)].shape[0]
    zone_counts[zone] = seconds

# === Normalized Power (NP) ===
rolling_power = df['power'].rolling(window=30, min_periods=30).mean() ** 4
np_value = rolling_power.mean() ** 0.25 if not rolling_power.empty else 0

# === Intensity Factor (IF) ===
if_value = np_value / FTP

# === Training Stress Score (TSS) ===
duration_minutes = len(df) / 60
tss = (duration_minutes * np_value * if_value) / (FTP * 60) * 100

# === Output ===
print("\n📊 Time in Power Zones:")
total_seconds = sum(zone_counts.values())
for zone, seconds in zone_counts.items():
    pct = (seconds / total_seconds) * 100 if total_seconds > 0 else 0
    print(f" - {zone}: {seconds} sec ({pct:.1f}%)")

print(f"\n⚡ Normalized Power (NP): {np_value:.0f} W")
print(f"🔥 Intensity Factor (IF): {if_value:.2f}")
print(f"📈 Training Stress Score (TSS): {tss:.1f}")
