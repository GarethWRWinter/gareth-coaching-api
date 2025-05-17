# scripts/calculate_tss.py
import pandas as pd
import numpy as np

def calculate_tss(df: pd.DataFrame, ftp: int) -> float:
    """
    Calculate Training Stress Score (TSS).
    TSS = (sec * NP * IF) / (FTP * 3600) * 100
    """
    if df.empty or 'power' not in df.columns:
        return 0.0

    # Drop NaNs and clip bad data
    power_data = df['power'].dropna().astype(float)
    if power_data.empty:
        return 0.0

    # Time diff per row in seconds
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    df['time_diff'] = df['timestamp'].diff().dt.total_seconds().fillna(0)
    df['time_diff'] = df['time_diff'].clip(lower=0, upper=10)

    # Normalized Power (NP)
    rolling_avg = power_data.rolling(window=30, min_periods=1).mean() ** 4
    np_value = (rolling_avg.mean()) ** 0.25 if not rolling_avg.empty else 0

    # Intensity Factor (IF)
    IF = np_value / ftp if ftp > 0 else 0

    # Total time in seconds
    total_time = df['time_diff'].sum()

    # TSS Calculation
    tss = ((total_time * np_value * IF) / (ftp * 3600)) * 100 if ftp > 0 else 0
    return round(tss, 2)
