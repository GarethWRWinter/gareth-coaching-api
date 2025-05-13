import os
from fitparse import FitFile
from datetime import datetime
from scripts.ride_database import save_ride_summary
from scripts.refresh_token import refresh_token as get_dropbox_access_token
import dropbox
import io
import numpy as np

FTP = 308  # ✅ Gareth's current FTP

def calculate_tss(duration_seconds, avg_power):
    intensity_factor = avg_power / FTP
    tss = (duration_seconds * avg_power * intensity_factor) / (FTP * 3600) * 100
    return round(tss, 1)

def calculate_power_zones(power_series):
    zones = {
        "zone1": (0, 0.55 * FTP),
        "zone2": (0.55 * FTP, 0.75 * FTP),
        "zone3": (0.75 * FTP, 0.90 * FTP),
        "zone4": (0.90 * FTP, 1.05 * FTP),
        "zone5": (1.05 * FTP, 1.20 * FTP),
        "zone6": (1.20 * FTP, float("inf"))
    }

    seconds_in_zones = {zone: 0 for zone in zones}

    for power in power_series:
        for zone, (low, high) in zones.items():
            if low <= power < high:
                seconds_in_zones[zone] += 1
                break

    total = len(power_series)
    zone_data = {}
    for zone in zones:
        sec = seconds_in_zones[zone]
        zone_data[f"{zone}_s"] = sec
        zone_data[f"{zone}_min"] = round(sec / 60, 1)
        zone_data[f"{zone}_pct"] = round(100 * sec / total, 1)

    return zone_data

def process_latest_fit_file(dbx_path):
    access_token = get_dropbox_access_token()
    dbx = dropbox.Dropbox(access_token)
    metadata, res = dbx.files_download(dbx_path)
    fitfile = FitFile(io.BytesIO(res.content))
    records = [r for r in fitfile.get_messages("record")]

    power_series = []
    heart_rate_series = []

    for record in records:
        power = record.get_value("power")
        hr = record.get_value("heart_rate")
        if power is not None:
            power_series.append(power)
        if hr is not None:
            heart_rate_series.append(hr)

    if not records:
        raise ValueError("No record data found in FIT file")

    timestamp = records[0].get_value("timestamp")
    duration_seconds = len(power_series)
    avg_power = round(np.mean(power_series), 1) if power_series else 0
    max_power = round(np.max(power_series), 1) if power_series else 0
    avg_hr = round(np.mean(heart_rate_series), 1) if heart_rate_series else 0
    max_hr = round(np.max(heart_rate_series), 1) if heart_rate_series else 0
    tss = calculate_tss(duration_seconds, avg_power)
    time_in_zones = calculate_power_zones(power_series)

    summary = {
        "filename": os.path.basename(dbx_path),
        "rows": len(records),
        "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        "duration_s": duration_seconds,
        "avg_power": avg_power,
        "max_power": max_power,
        "avg_heart_rate": avg_hr,
        "max_heart_rate": max_hr,
        "tss": tss,
        "time_in_zones": time_in_zones
    }

    save_ride_summary(summary)
    return summary
