import os
import dropbox
import pandas as pd
import numpy as np
from fitparse import FitFile
from scripts.ride_database import save_ride_summary
from scripts.refresh_token import get_dropbox_access_token
from io import BytesIO
from datetime import timedelta

def calculate_tss(power_series, ftp, duration_seconds):
    normalized_power = np.power(np.mean(np.power(power_series, 4)), 0.25)
    intensity_factor = normalized_power / ftp
    tss = (duration_seconds * normalized_power * intensity_factor) / (ftp * 3600) * 100
    return round(tss, 1)

def calculate_time_in_zones(power_series, ftp):
    zones = {
        "zone1": (0, 0.55 * ftp),
        "zone2": (0.55 * ftp, 0.75 * ftp),
        "zone3": (0.75 * ftp, 0.9 * ftp),
        "zone4": (0.9 * ftp, 1.05 * ftp),
        "zone5": (1.05 * ftp, 1.2 * ftp),
        "zone6": (1.2 * ftp, float("inf")),
    }

    total_seconds = len(power_series)
    result = {}

    for zone, (low, high) in zones.items():
        zone_seconds = np.sum((power_series >= low) & (power_series < high))
        zone_minutes = round(zone_seconds / 60, 1)
        zone_pct = round(zone_seconds / total_seconds * 100, 1)
        result[f"{zone}_s"] = int(zone_seconds)
        result[f"{zone}_min"] = zone_minutes
        result[f"{zone}_pct"] = zone_pct

    return result

def process_latest_fit_file(access_token, ftp=308):
    dbx = dropbox.Dropbox(access_token)
    folder = os.environ.get("DROPBOX_FOLDER", "")
    entries = dbx.files_list_folder(folder).entries
    fit_files = [f for f in entries if f.name.endswith(".fit")]
    latest_file = sorted(fit_files, key=lambda x: x.server_modified, reverse=True)[0]
    metadata, res = dbx.files_download(latest_file.path_display)

    fitfile = FitFile(BytesIO(res.content))
    records = [r.get_values() for r in fitfile.get_messages("record")]
    df = pd.DataFrame(records)

    if "timestamp" not in df or df.empty:
        raise ValueError("Invalid or empty FIT file")

    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["power"] = df["power"].fillna(0).astype(int)
    df["heart_rate"] = df["heart_rate"].fillna(0).astype(int)

    start_time = df["timestamp"].iloc[0]
    duration_s = int((df["timestamp"].iloc[-1] - df["timestamp"].iloc[0]).total_seconds())
    avg_power = round(df["power"].mean(), 1)
    max_power = int(df["power"].max())
    avg_hr = round(df["heart_rate"].mean(), 1)
    max_hr = int(df["heart_rate"].max())
    tss = calculate_tss(df["power"].values, ftp, duration_s)
    zones = calculate_time_in_zones(df["power"].values, ftp)

    result = {
        "filename": latest_file.name,
        "rows": len(df),
        "timestamp": start_time.strftime("%Y-%m-%d %H:%M:%S"),
        "duration_s": duration_s,
        "avg_power": avg_power,
        "max_power": max_power,
        "avg_heart_rate": avg_hr,
        "max_heart_rate": max_hr,
        "tss": tss,
        "time_in_zones": zones
    }

    save_ride_summary(result)
    return result
