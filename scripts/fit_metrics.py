# scripts/fit_metrics.py

import pandas as pd
import hashlib

def calculate_ride_metrics(df: pd.DataFrame) -> dict:
    if isinstance(df, list):
        return {"error": "Expected DataFrame, got list."}
    if df.empty:
        return {"error": "No data in FIT file."}

    df = df.dropna(subset=["timestamp"])

    # Core duration
    duration_seconds = (df["timestamp"].max() - df["timestamp"].min()).total_seconds()
    distance_km = df["distance"].max() / 1000 if "distance" in df else None

    # Helpers
    def safe_avg(col): return float(df[col].mean()) if col in df else None
    def safe_max(col): return float(df[col].max()) if col in df else None

    # Time in zones
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

    # Define zones
    power_zones = [(0, 120), (120, 160), (160, 200), (200, 240), (240, 280), (280, 320), (320, 2000)]
    hr_zones = [(0, 110), (110, 130), (130, 150), (150, 170), (170, 190), (190, 220)]

    # Generate ride_id from timestamp hash
    ride_start = df["timestamp"].min()
    ride_id = hashlib.md5(str(ride_start).encode()).hexdigest()

    return {
        "ride_id": ride_id,
        "timestamp": str(ride_start),
        "duration_seconds": int(duration_seconds),
        "duration_minutes": round(duration_seconds / 60, 1),
        "distance": round(distance_km, 2) if distance_km else None,
        "avg_power": safe_avg("power"),
        "max_power": safe_max("power"),
        "avg_hr": safe_avg("heart_rate"),
        "max_hr": safe_max("heart_rate"),
        "avg_cadence": safe_avg("cadence"),
        "max_cadence": safe_max("cadence"),
        "training_stress_score": safe_avg("tss"),
        "normalized_power": safe_avg("normalized_power"),
        "variability_index": safe_avg("variability_index"),
        "pedal_balance": safe_avg("left_right_balance"),
        "time_in_zones": {
            "power": time_in_zones("power", power_zones),
            "heart_rate": time_in_zones("heart_rate", hr_zones)
        }
    }
