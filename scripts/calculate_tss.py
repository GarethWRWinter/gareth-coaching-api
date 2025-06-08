# scripts/calculate_tss.py

import numpy as np
from scripts.constants import FTP

print(f"[INFO] Using FTP in calculate_tss: {FTP}")

def calculate_normalized_power(power_series):
    """
    Calculate Normalized Power (NP):
    - 30-second rolling average of the power data
    - Each 30s average raised to the 4th power
    - Mean of these, then take the 4th root
    """
    if len(power_series) < 30:
        np_power = np.mean(power_series)
        print("[WARN] Power series too short for 30s NP. Using avg_power as NP.")
        return np_power

    # Rolling 30-second average
    rolling_30s = np.convolve(power_series, np.ones(30) / 30, mode='valid')

    # 4th power transformation
    rolling_30s_4th = rolling_30s ** 4

    # Mean of 4th powers and final 4th root
    avg_4th_power = np.mean(rolling_30s_4th)
    np_power = avg_4th_power ** (1 / 4)

    print(f"[INFO] Calculated Normalized Power: {np_power:.2f} watts")
    return np_power

def calculate_tss(power_series, duration_sec):
    """
    Calculate Training Stress Score (TSS):
    - Uses Normalized Power (NP)
    - Uses Intensity Factor (IF = NP / FTP)
    - Formula: TSS = (duration * NP * IF) / (FTP * 3600) * 100
    """
    avg_power = np.mean(power_series)
    np_power = calculate_normalized_power(power_series)
    intensity_factor = np_power / FTP
    tss = (duration_sec * np_power * intensity_factor) / (FTP * 3600) * 100

    print(f"[INFO] Calculated TSS: {tss:.2f} (NP: {np_power:.2f}, IF: {intensity_factor:.2f}, FTP: {FTP})")
    return tss
