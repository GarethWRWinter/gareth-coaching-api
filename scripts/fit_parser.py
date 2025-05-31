import pandas as pd
import numpy as np
from scripts.time_in_zones import calculate_time_in_zones

def calculate_ride_metrics(df, ftp):
    # Ensure power data is numeric
    df["power"] = pd.to_numeric(df["power"], errors="coerce")
    df = df.dropna(subset=["power"])

    duration_seconds = (df["timestamp"].iloc[-1] - df["timestamp"].iloc[0]).total_seconds()
    average_power = df["power"].mean()
    max_power = df["power"].max()

    # Compute TSS
    intensity_factor = average_power / ftp
    tss = (duration_seconds * average_power * intensity_factor) / (ftp * 3600) * 100

    # Time in zones
    zones_data = calculate_time_in_zones(df, ftp)

    return {
        "duration_seconds": duration_seconds,
        "average_power": average_power,
        "max_power": max_power,
        "tss": tss,
        "zones": zones_data,
    }
