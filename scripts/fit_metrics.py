import pandas as pd


def calculate_ride_metrics(df):
    if not isinstance(df, pd.DataFrame) or df.empty:
        return {"error": "FIT file contained no ride data."}

    # ✅ Handle missing columns gracefully
    duration = len(df) if "timestamp" in df.columns else 0
    avg_power = df["power"].mean() if "power" in df.columns else None
    avg_hr = df["heart_rate"].mean() if "heart_rate" in df.columns else None
    avg_cadence = df["cadence"].mean() if "cadence" in df.columns else None
    max_power = df["power"].max() if "power" in df.columns else None
    total_kj = df["power"].sum() * 1 / 1000 if "power" in df.columns else None

    # Return all keys, even if None
    return {
        "duration": duration,
        "avg_power": round(avg_power, 2) if avg_power is not None else None,
        "avg_heart_rate": round(avg_hr, 2) if avg_hr is not None else None,
        "avg_cadence": round(avg_cadence, 2) if avg_cadence is not None else None,
        "max_power_
