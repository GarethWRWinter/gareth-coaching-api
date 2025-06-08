# scripts/fit_parser.py
import pandas as pd
import numpy as np
from scripts.time_in_zones import calculate_time_in_zones
from scripts.constants import FTP

def calculate_normalized_power(power_series):
    """Calculate Normalized Power (NP) using a 30-sec rolling average and 4th power mean."""
    rolling_power = power_series.rolling(window=30, min_periods=1, center=True).mean()
    rolling_power_4th = rolling_power.pow(4)
    mean_rolling_power_4th = rolling_power_4th.mean()
    np_power = mean_rolling_power_4th ** (1/4)
    return np_power

def calculate_ride_metrics(df, ftp=FTP):
    print(f"[INFO] Using FTP for metrics: {ftp}")
    df["power"] = pd.to_numeric(df["power"], errors="coerce").fillna(0)
    df = df.dropna(subset=["power"])
    
    duration_seconds = (df["timestamp"].iloc[-1] - df["timestamp"].iloc[0]).total_seconds()
    average_power = df["power"].mean()
    max_power = df["power"].max()
    np_power = calculate_normalized_power(df["power"])
    intensity_factor = np_power / ftp
    tss = (duration_seconds * np_power * intensity_factor) / (ftp * 3600) * 100

    print(f"[INFO] Metrics: Duration {duration_seconds:.1f}s | Avg Power {average_power:.1f}W | NP {np_power:.1f}W | TSS {tss:.1f}")
    
    zones_data = calculate_time_in_zones(df, ftp)

    return {
        "duration_seconds": duration_seconds,
        "average_power": average_power,
        "max_power": max_power,
        "normalized_power": np_power,
        "tss": tss,
        "zones": zones_data,
    }
