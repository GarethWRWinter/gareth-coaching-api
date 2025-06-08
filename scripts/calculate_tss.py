# scripts/calculate_tss.py
import numpy as np
from scripts.constants import FTP

def calculate_normalized_power(power_series, window=30):
    """
    Calculate Normalized Power (NP) following TrainingPeaks' methodology.
    """
    rolling_avg = power_series.rolling(window=window, min_periods=1).mean()
    fourth_power = rolling_avg.pow(4)
    avg_fourth_power = fourth_power.mean()
    normalized_power = avg_fourth_power ** 0.25
    return normalized_power

def calculate_tss(df):
    """
    Calculate Training Stress Score (TSS) using NP, FTP, and ride duration.
    """
    # Clean power data
    power = df["power"].astype(float).fillna(0)

    # Calculate NP
    np_value = calculate_normalized_power(power)
    
    # Calculate Intensity Factor (IF)
    intensity_factor = np_value / FTP
    
    # Ride duration in seconds
    duration_sec = len(power)
    
    # Calculate TSS
    tss = (duration_sec * np_value * intensity_factor) / (FTP * 3600) * 100
    
    # Logging for diagnosis
    print(f"[INFO] NP: {np_value:.2f} | IF: {intensity_factor:.2f} | TSS: {tss:.2f}")
    
    return tss, np_value, intensity_factor
