import numpy as np
from collections import defaultdict

def calculate_ride_metrics(fit_df):
    """
    Compute key ride metrics from the parsed FIT dataframe.
    Includes basic metrics and left/right pedal balance.
    """
    summary = {}

    if fit_df.empty:
        return summary

    # Start & duration
    summary["start_time"] = fit_df["timestamp"].iloc[0].isoformat()
    summary["duration_s"] = len(fit_df)

    # Power & heart rate
    summary["avg_power"] = int(np.nanmean(fit_df.get("power", np.nan)))
    summary["max_power"] = int(np.nanmax(fit_df.get("power", np.nan)))
    summary["avg_hr"] = int(np.nanmean(fit_df.get("heart_rate", np.nan)))
    summary["max_hr"] = int(np.nanmax(fit_df.get("heart_rate", np.nan)))
    summary["avg_cadence"] = int(np.nanmean(fit_df.get("cadence", np.nan)))

    # TSS (Training Stress Score) – simple estimation
    ftp = 308  # You can make this dynamic later
    norm_power = (np.mean(np.power(fit_df.get("power", np.nan), 4)))**0.25
    intensity = norm_power / ftp if ftp > 0 else 0
    duration_hr = len(fit_df) / 3600
    tss = duration_hr * intensity**2 * 100
    summary["tss"] = round(tss, 1)

    # Pedal balance
    left = fit_df.get("left_right_balance", np.nan)
    if not np.isnan(left).all():
        left_clean = left[left > 0]
        if len(left_clean) > 0:
            left_percent = int(np.nanmean(left_clean) * 100 / 255)
            right_percent = 100 - left_percent
            summary["pedal_balance"] = {
                "left": left_percent,
                "right": right_percent
            }

    return summary
