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
    zones = get_power_zones(ftp)  # ✅ Ensure zones is a dict

    time_in_zone = {zone: 0 for zone in zones.keys()}  # ✅ FIXED

    for i in range(1, len(df)):
        power = df.at[i, "power"]
        duration = df.iloc[i]["timestamp"] - df.iloc[i - 1]["timestamp"]
        duration_seconds = duration.total_seconds()

        for zone, (low, high) in zones.items():
            if low <= power < high:
                time_in_zone[zone] += duration_seconds
                break

    return {
        "seconds_per_zone": time_in_zone,
        "minutes_per_zone": {k: round(v / 60, 2) for k, v in time_in_zone.items()},
    }
