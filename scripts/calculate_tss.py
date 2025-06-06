import pandas as pd
from scripts.constants import FTP

# Logging to confirm FTP usage
print(f"✅ Using FTP for TSS calculation: {FTP} watts")

def calculate_tss(df: pd.DataFrame) -> float:
    if "power" not in df.columns:
        print("⚠️ No power data found in DataFrame.")
        return 0.0

    # Drop missing power values
    df = df.dropna(subset=["power"])

    # Compute 30s rolling average for normalized power
    rolling_power = df["power"].rolling(window=30, min_periods=1).mean()
    normalized_power = (rolling_power ** 4).mean() ** 0.25

    # Logging normalized power
    print(f"ℹ️ Normalized Power: {normalized_power}")

    intensity_factor = normalized_power / FTP if FTP > 0 else 0
    duration_hours = (df["timestamp"].iloc[-1] - df["timestamp"].iloc[0]).total_seconds() / 3600.0

    tss = (duration_hours * normalized_power * intensity_factor) / (FTP * 3600.0) * 100.0 if FTP > 0 else 0.0

    # Logging final TSS calculation
    print(f"ℹ️ Calculated TSS: {tss}")
    return round(tss, 2)
