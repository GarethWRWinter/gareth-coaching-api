import os
import dropbox
import io
import logging
import pandas as pd
from fitparse import FitFile
from scripts.calculate_power_zones import get_power_zones
from scripts.calculate_tss import calculate_tss
from scripts.time_in_zones import compute_time_in_power_zones, compute_time_in_hr_zones
from scripts.sanitize import sanitize_fit_data
from scripts.dropbox_auth import refresh_dropbox_token

logger = logging.getLogger(__name__)

DROPBOX_FOLDER = os.getenv("DROPBOX_FOLDER", "/Apps/WahooFitness")
FTP = int(os.getenv("FTP", "308"))

def process_latest_fit_file(_: str = None):
    try:
        access_token = refresh_dropbox_token()
        dbx = dropbox.Dropbox(access_token)
        files = dbx.files_list_folder(DROPBOX_FOLDER).entries
        fit_files = [f for f in files if f.name.endswith(".fit")]

        if not fit_files:
            raise FileNotFoundError("No .FIT files found in Dropbox folder.")

        latest_file = sorted(fit_files, key=lambda x: x.client_modified, reverse=True)[0]
        _, res = dbx.files_download(latest_file.path_lower)
        fit = FitFile(io.BytesIO(res.content))
        fit.parse()

        records = []
        for record in fit.get_messages("record"):
            fields = {field.name: field.value for field in record}
            if "timestamp" in fields:
                records.append(fields)

        df = pd.DataFrame(records)
        df = sanitize_fit_data(df)

        if df.empty:
            raise ValueError("Parsed FIT data is empty.")

        duration_sec = (df["timestamp"].iloc[-1] - df["timestamp"].iloc[0]).total_seconds()
        duration_min = round(duration_sec / 60, 1)

        avg_power = int(df["power"].mean())
        max_power = int(df["power"].max())
        avg_hr = int(df["heart_rate"].mean())
        max_hr = int(df["heart_rate"].max())
        avg_cadence = int(df["cadence"].mean())
        start_time = df["timestamp"].iloc[0].strftime("%Y-%m-%d %H:%M:%S")
        ride_id = df["timestamp"].iloc[0].strftime("%Y%m%d_%H%M%S")

        power_zones = get_power_zones(FTP)
        time_in_power = compute_time_in_power_zones(df["power"], power_zones)
        time_in_hr = compute_time_in_hr_zones(df["heart_rate"])
        tss, np, intensity = calculate_tss(df["power"].values, FTP)

        full_data = df.to_dict(orient="records")

        summary = {
            "ride_id": ride_id,
            "start_time": start_time,
            "duration_min": duration_min,
            "avg_power": avg_power,
            "max_power": max_power,
            "avg_heart_rate": avg_hr,
            "max_heart_rate": max_hr,
            "avg_cadence": avg_cadence,
            "tss": round(tss, 1),
            "normalized_power": round(np, 1),
            "intensity_factor": round(intensity, 2),
            "time_in_power_zones_sec": time_in_power,
            "time_in_hr_zones_sec": time_in_hr,
            "full_data": full_data,
        }

        return sanitize_fit_data(summary)

    except Exception as e:
        logger.exception("Error processing latest FIT file")
        raise
