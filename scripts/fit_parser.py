import pandas as pd
from fitparse import FitFile
from datetime import timedelta
from scripts.time_in_zones import calculate_time_in_zones
from scripts.calculate_tss import calculate_tss
from scripts.sanitize import sanitize


def parse_fit(file_path: str) -> pd.DataFrame:
    """
    Parse a FIT file into a clean Pandas DataFrame with key metrics.
    """
    fitfile = FitFile(file_path)
    records = []

    for record in fitfile.get_messages("record"):
        record_data = {}
        for data in record:
            record_data[data.name] = data.value
        records.append(record_data)

    df = pd.DataFrame(records)

    if "timestamp" in df.columns:
        df = df.dropna(subset=["timestamp"])
        df = df.sort_values("timestamp")
        df.reset_index(drop=True, inplace=True)

    return df


def calculate_ride_metrics(df: pd.DataFrame, ftp: int = 250) -> dict:
    """
    Given a DataFrame of FIT data, calculate key ride summary metrics.
    """
    if df.empty:
        return {"error": "No data in ride file"}

    df = df.dropna(subset=["timestamp"])
    df = df.sort_values(by="timestamp")
    df.reset_index(drop=True, inplace=True)

    duration_seconds = (df["timestamp"].iloc[-1] - df["timestamp"].iloc[0]).total_seconds()
    total_distance_km = df["distance"].max() / 1000 if "distance" in df.columns else None

    avg_power = df["power"].mean() if "power" in df.columns else None
    max_power = df["power"].max() if "power" in df.columns else None
    avg_hr = df["heart_rate"].mean() if "heart_rate" in df.columns else None
    max_hr = df["heart_rate"].max() if "heart_rate" in df.columns else None
    avg_cadence = df["cadence"].mean() if "cadence" in df.columns else None
    max_cadence = df["cadence"].max() if "cadence" in df.columns else None

    tss = calculate_tss(df, ftp) if "power" in df.columns else None
    time_in_zones = calculate_time_in_zones(df, ftp) if "power" in df.columns else {}

    summary = {
        "ride_id": df["timestamp"].iloc[0].isoformat(),
        "start_time": df["timestamp"].iloc[0].isoformat(),
        "duration_seconds": duration_seconds,
        "total_distance_km": total_distance_km,
        "avg_power": avg_power,
        "max_power": max_power,
        "avg_heart_rate": avg_hr,
        "max_heart_rate": max_hr,
        "avg_cadence": avg_cadence,
        "max_cadence": max_cadence,
        "tss": tss,
        "time_in_zones": time_in_zones,
    }

    return sanitize(summary)
