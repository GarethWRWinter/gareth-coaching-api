import pandas as pd

def calculate_time_in_zones(data: pd.DataFrame, ftp: int) -> dict:
    """Calculate time spent in each power zone based on FTP."""
    power_zones = {
        "Z1 (Recovery)": (0, 0.55 * ftp),
        "Z2 (Endurance)": (0.55 * ftp, 0.75 * ftp),
        "Z3 (Tempo)": (0.75 * ftp, 0.9 * ftp),
        "Z4 (Threshold)": (0.9 * ftp, 1.05 * ftp),
        "Z5 (VO2 Max)": (1.05 * ftp, 1.2 * ftp),
        "Z6 (Anaerobic)": (1.2 * ftp, 1.5 * ftp),
        "Z7 (Neuromuscular)": (1.5 * ftp, float("inf")),
    }

    # Ensure timestamp is datetime
    data['timestamp'] = pd.to_datetime(data['timestamp'])

    # Calculate duration per sample (assuming roughly 1s recording rate)
    data['duration'] = data['timestamp'].diff().dt.total_seconds().fillna(1)

    # Replace any missing power values with 0
    data['power'] = pd.to_numeric(data['power'], errors='coerce').fillna(0)

    time_in_zones = {}

    for zone, (low, high) in power_zones.items():
        mask = (data['power'] >= low) & (data['power'] < high)
        time_sec = data.loc[mask, 'duration'].sum()
        time_in_zones[zone] = {
            "seconds": round(time_sec),
            "minutes": round(time_sec / 60, 1),
        }

    return time_in_zones
