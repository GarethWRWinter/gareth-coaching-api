# scripts/calculate_tss.py
import numpy as np
from scripts.constants import FTP

def calculate_normalized_power(power_series):
    """
    Calculate Normalized Power (NP) as a 30-second rolling average to the 4th power.
    """
    if len(power_series) < 30:
        return np.mean(power_series)

    rolling_30s = np.convolve(power_series, np.ones(30) / 30, mode='valid')
    rolling_30s_4th = rolling_30s ** 4
    avg_4th_root = np.mean(rolling_30s_4th) ** (1 / 4)
    return avg_4th_root

def calculate_tss(duration_sec, power_series):
    """
    Calculate Training Stress Score (TSS) for a ride.
    """
    np_power = calculate_normalized_power(power_series)
    intensity_factor = np_power / FTP
    tss = (duration_sec * np_power * intensity_factor) / (FTP * 3600) * 100

    # Logging for debugging
    print(f"🚴‍♂️ FTP: {FTP} watts")
    print(f"🚴‍♂️ Normalized Power: {np_power:.2f} watts")
    print(f"🚴‍♂️ Intensity Factor (IF): {intensity_factor:.3f}")
    print(f"🚴‍♂️ TSS: {tss:.2f}")

    return tss
