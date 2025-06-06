import numpy as np
import pandas as pd
from scripts.constants import FTP

# Logging to confirm FTP usage
print(f"✅ Using FTP for fit metrics: {FTP} watts")

def calculate_ride_metrics(df: pd.DataFrame):
    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df.sort_values("timestamp", inplace=True)
    df.reset_index(drop=True, inplace=True)

    # Drop missing values
    df["power"] = pd.to_numeric(df.get("power", 0), errors="coerce").fillna(0)
    df["heart_rate"] = pd.to_numeric(df.get("heart_rate", 0), errors="coerce").fillna(0)
    df["cadence"] = pd.to_numeric(df.get("cadence", 0), errors="coerce").fillna(0)
    df["left_right_balance"] = pd.to_numeric(df.get("left_right_balance", np.nan), errors="coerce")

    duration_sec = (df["timestamp"].iloc[-1] - df["timestamp"].iloc[0]).total_seconds()
    avg_power = df["power"].mean()
    max_power = df["power"].max()
    avg_hr = df["heart_rate"].mean()
    max_hr = df["heart_rate"].max()
    avg_cad = df["cadence"].mean()

    # Normalized Power (NP)
    rolling_30 = df["power"].rolling(window=30, min_periods=1).mean()
    np_power = (rolling_30 ** 4).mean() ** 0.25
    print(f"ℹ️ Normalized Power: {np_power}")

    # Intensity Factor (IF) and TSS
    intensity_factor = np_power / FTP if FTP > 0 else 0
    tss = (duration_sec * np_power * intensity_factor) / (FTP * 3600) * 100 if FTP > 0 else 0
    print(f"ℹ️ Intensity Factor: {intensity_factor}, Calculated TSS: {tss}")

    # Power zones
    power_zones = {
        "Z1 (<55%)": (0, 0.55 * FTP),
        "Z2 (55–75%)": (0.55 * FTP, 0.75 * FTP),
        "Z3 (75–90%)": (0.75 * FTP, 0.9 * FTP),
        "Z4 (90–105%)": (0.9 * FTP, 1.05 * FTP),
        "Z5 (105–120%)": (1.05 * FTP, 1.2 * FTP),
        "Z6 (120–150%)": (1.2 * FTP, 1.5 * FTP),
        "Z7 (>150%)": (1.5 * FTP, np.inf),
    }

    time_in_zones = {}
    for zone, (low, high) in power_zones.items():
        seconds = df[(df["power"] >= low) & (df["power"] < high)].shape[0]
        time_in_zones[zone] = {
            "seconds": int(seconds),
            "minutes": round(seconds / 60, 1)
        }

    avg_lr_balance = df["left_right_balance"].mean() if df["left_right_balance"].notna().any() else None

    summary = {
        "ride_id": df["timestamp"].iloc[0].strftime("%Y%m%d_%H%M%S"),
        "start_time": df["timestamp"].iloc[0].isoformat(),
        "duration_sec": int(duration_sec),
        "avg_power": round(avg_power, 1),
        "max_power": int(max_power),
        "np": round(np_power, 1),
        "if": round(intensity_factor, 3),
        "tss": round(tss, 1),
        "avg_hr": round(avg_hr, 1),
        "max_hr": int(max_hr),
        "avg_cad": round(avg_cad, 1),
        "time_in_zones": time_in_zones,
        "pedal_balance": round(avg_lr_balance, 1) if avg_lr_balance else None,
    }

    data_records = df.to_dict(orient="records")
    return summary, data_records
