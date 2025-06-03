import pandas as pd
from scripts.constants import FTP

print(f"✅ Using FTP for TSS calculation: {FTP}")

def calculate_tss(df: pd.DataFrame) -> float:
    if "power" not in df.columns:
        return 0.0

    # Drop any rows where power is missing
    df = df.dropna(subset=["power"])

    # Compute normalized power (30s rolling avg)
    rolling_power = df["power"].rolling(window=30, min_periods=1).mean()
    normalized_power = (rolling_power ** 4).mean() ** 0.25

    intensity_factor = normalized_power / FTP
    duration_hours = (df["timestamp"].iloc[-1] - df["timestamp"].iloc[0]).total_seconds() / 3600.0

    tss = (duration_hours * normalized_power * intensity_factor) / (FTP * 3600.0) * 100.0
    return round(tss, 2)
