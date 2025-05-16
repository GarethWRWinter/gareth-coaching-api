# scripts/fit_metrics.py

import pandas as pd

def calculate_ride_metrics(df: pd.DataFrame) -> dict:
    if df.empty:
        return {"error": "No data in FIT file."}

    # Drop rows with missing timestamps
    df = df.dropna(subset=["timestamp"])

    # Basic stats
    duration_seconds = (df["timestamp"].max() - df["timestamp"].min()).total_seconds()
    total_distance_km = df["distance"].max() / 1000 if "distance" in df else None

    def safe_avg(col):
        return float(df[col].mean()) if col in df else None

    def safe_max(col):
        return float(df[col].max()) if col in df else None

    # Zones (basic threshold defaults, you may replace later)
    def time_in_zones(column: str, zones: list[tuple[int, int]]) -> dict:
        if column not in df:
            return {}
        out = {}
        for i, (low, high) in enumerate(zones, 1):
            zone_df = df[(df[column] >= low) & (df[column] < high)]
            seconds = len(zone_df)
            out[f"Z{i}"] = {
                "seconds": seconds,
                "minutes": round(seconds / 60, 1)
            }
        return out

    power_zones = [(0, 120), (120, 160), (160, 200), (200, 240), (240, 280), (280, 320), (320, 2000)]
    hr_zones = [(0, 110), (110, 130), (130, 150), (150, 170), (170, 190), (190, 220)]

    return {
        "duration_seconds": int(duration_seconds),
        "duration_minutes": round(duration_seconds / 60, 1),
        "distance_km": round(total_distance_km, 2) if total_distance_km else None,
        "avg_power": safe_avg("power"),
        "max_power": safe_max("power"),
        "avg_heart_rate": safe_avg("heart_rate"),
        "max_heart_rate": safe_max("heart_rate"),
        "avg_cadence": safe_avg("cadence"),
        "max_cadence": safe_max("cadence"),
        "power_zones": time_in_zones("power", power_zones),
        "heart_rate_zones": time_in_zones("heart_rate", hr_zones)
    }
