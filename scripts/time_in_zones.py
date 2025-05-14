import pandas as pd
import numpy as np

def calculate_time_in_zones(df: pd.DataFrame, ftp: int) -> dict:
    # Filter valid power rows
    valid_df = df[df['power'].notna()].copy()

    # Define zone boundaries based on FTP
    zones = {
        'Z1_Recovery': (0, 0.55 * ftp),
        'Z2_Endurance': (0.55 * ftp, 0.75 * ftp),
        'Z3_Tempo': (0.75 * ftp, 0.90 * ftp),
        'Z4_Threshold': (0.90 * ftp, 1.05 * ftp),
        'Z5_VO2Max': (1.05 * ftp, 1.20 * ftp),
        'Z6_Anaerobic': (1.20 * ftp, 1.50 * ftp),
        'Z7_Neuromuscular': (1.50 * ftp, float('inf'))
    }

    # Default to 1 second per row if timestamp not usable
    if 'timestamp' in valid_df.columns:
        valid_df['time_diff'] = valid_df['timestamp'].diff().dt.total_seconds().fillna(0)
        valid_df['time_diff'] = valid_df['time_diff'].clip(lower=0, upper=10)  # sanity bounds
    else:
        valid_df['time_diff'] = 1

    # Allocate time per zone
    time_in_zones = {}
    for zone, (low, high) in zones.items():
        mask = (valid_df['power'] >= low) & (valid_df['power'] < high)
        time_seconds = valid_df.loc[mask, 'time_diff'].sum()
        time_in_zones[zone] = {
            'seconds': round(float(time_seconds), 2),
            'minutes': round(float(time_seconds) / 60, 2)
        }

    return time_in_zones
