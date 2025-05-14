def calculate_time_in_zones(data: pd.DataFrame, ftp: int) -> dict:
    zones = {
        "Z1 (Recovery)": (0, 0.55 * ftp),
        "Z2 (Endurance)": (0.55 * ftp, 0.75 * ftp),
        "Z3 (Tempo)": (0.75 * ftp, 0.90 * ftp),
        "Z4 (Threshold)": (0.90 * ftp, 1.05 * ftp),
        "Z5 (VO2max)": (1.05 * ftp, 1.20 * ftp),
        "Z6 (Anaerobic)": (1.20 * ftp, 1.50 * ftp),
        "Z7 (Neuromuscular)": (1.50 * ftp, float('inf')),
    }

    time_in_zone = {zone: 0 for zone in zones}

    previous_timestamp = None
    for i, row in data.iterrows():
        timestamp = row["timestamp"]
        if pd.isnull(timestamp):
            continue
        if previous_timestamp is None:
            previous_timestamp = timestamp
            continue
        duration = timestamp - previous_timestamp
        duration_seconds = float(duration / np.timedelta64(1, 's'))  # ✅ CORRECTED

        for zone, (low, high) in zones.items():
            if low <= row["power"] < high:
                time_in_zone[zone] += duration_seconds
                break
        previous_timestamp = timestamp

    return time_in_zone
