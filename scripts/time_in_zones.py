# scripts/time_in_zones.py

def get_power_zones(ftp):
    return {
        "Z1": (0, 0.55 * ftp),
        "Z2": (0.55 * ftp, 0.75 * ftp),
        "Z3": (0.75 * ftp, 0.9 * ftp),
        "Z4": (0.9 * ftp, 1.05 * ftp),
        "Z5": (1.05 * ftp, 1.2 * ftp),
        "Z6": (1.2 * ftp, 1.5 * ftp),
        "Z7": (1.5 * ftp, float('inf')),
    }

def calculate_time_in_zones(df, ftp):
    zones = get_power_zones(ftp)
    time_in_zone = {zone: 0 for zone in zones.keys()}

    for i in range(1, len(df)):
        try:
            power = df.iloc[i]["power"]
            timestamp = df.iloc[i]["timestamp"]
            previous_timestamp = df.iloc[i - 1]["timestamp"]
            duration = timestamp - previous_timestamp
            duration_seconds = float(duration / np.timedelta64(1, 's'))  # ✅ CORRECTED

            for zone, (low, high) in zones.items():
                if low <= power < high:
                    time_in_zone[zone] += duration_seconds
                    break
        except Exception as e:
            continue

    # Format output
    return {
        zone: {
            "seconds": round(time, 2),
            "minutes": round(time / 60, 2)
        } for zone, time in time_in_zone.items()
    }
