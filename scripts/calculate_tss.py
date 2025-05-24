import numpy as np

def calculate_tss(power_data, ftp):
    if power_data is None or len(power_data) == 0:
        return 0, 0, 0

    # Convert to NumPy array if it's not
    power_data = np.array(power_data)

    # Calculate Normalized Power (NP)
    rolling_30s = np.convolve(power_data**4, np.ones(30)/30, mode='valid')
    np_ = np.power(np.mean(rolling_30s), 0.25) if len(rolling_30s) > 0 else 0

    # Calculate Intensity Factor (IF)
    intensity_factor = np_ / ftp if ftp else 0

    # Calculate TSS
    duration_hours = len(power_data) / 3600
    tss = duration_hours * (intensity_factor**2) * 100 if ftp else 0

    return tss, np_, intensity_factor
