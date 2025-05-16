import pandas as pd

def calculate_ride_metrics(df: pd.DataFrame) -> dict:
    if not isinstance(df, pd.DataFrame) or df.empty:
        return {
            "duration": 0,
            "avg_power": 0,
            "avg_heart_rate": 0,
            "avg_cadence": 0,
            "max_power": 0,
            "max_heart_rate": 0,
            "max_cadence": 0,
            "total_distance_km": 0,
            "total_work_kj": 0
        }

    duration = (df["timestamp"].iloc[-1] - df["timestamp"].iloc[0]).total_seconds()
    avg_power = df.get("power", pd.Series([0])).mean()
    avg_heart_rate = df.get("heart_rate", pd.Series([0])).mean()
    avg_cadence = df.get("cadence", pd.Series([0])).mean()
    max_power = df.get("power", pd.Series([0])).max()
    max_heart_rate = df.get("heart_rate", pd.Series([0])).max()
    max_cadence = df.get("cadence", pd.Series([0])).max()
    total_distance_km = df.get("distance", pd.Series([0])).max() / 1000
    total_work_kj = df.get("power", pd.Series([0])).sum() * (1/60/60)  # Power in watts * hours = kJ

    return {
        "duration": round(duration, 2),
        "avg_power": round(avg_power, 2),
        "avg_heart_rate": round(avg_heart_rate, 2),
        "avg_cadence": round(avg_cadence, 2),
        "max_power": int(max_power),
        "max_heart_rate": int(max_heart_rate),
        "max_cadence": int(max_cadence),
        "total_distance_km": round(total_distance_km, 2),
        "total_work_kj": round(total_work_kj, 2)
    }
