import os
import dropbox
import pandas as pd
from fitparse import FitFile
from datetime import datetime
from scripts.dropbox_auth import refresh_access_token
from scripts.ride_database import save_ride_summary
from scripts.time_in_zones import calculate_time_in_zones
from scripts.sanitize import sanitize_dict

DROPBOX_FOLDER = os.getenv("DROPBOX_FOLDER", "/Apps/WahooFitness")

def get_latest_dropbox_file_path(dbx, folder_path):
    entries = dbx.files_list_folder(folder_path).entries
    fit_files = [f for f in entries if f.name.endswith(".fit")]
    latest_file = max(fit_files, key=lambda f: f.client_modified)
    return latest_file.path_display

def parse_fit_file(file_stream):
    fitfile = FitFile(file_stream)
    records = [record.get_values() for record in fitfile.get_messages("record")]
    df = pd.DataFrame(records)

    session = list(fitfile.get_messages("session"))[0].get_values()
    ftp = session.get("threshold_power", 250)

    summary = {
        "start_time": session.get("start_time"),
        "duration_sec": session.get("total_timer_time"),
        "distance_km": session.get("total_distance", 0) / 1000,
        "avg_speed_kph": session.get("avg_speed", 0) * 3.6,
        "avg_power": session.get("avg_power"),
        "max_power": session.get("max_power"),
        "normalized_power": session.get("normalized_power"),
        "intensity_factor": session.get("intensity_factor"),
        "tss": session.get("training_stress_score"),
        "avg_hr": session.get("avg_heart_rate"),
        "max_hr": session.get("max_heart_rate"),
        "avg_cadence": session.get("avg_cadence"),
        "max_cadence": session.get("max_cadence"),
        "ftp_used": ftp,
    }

    zones = calculate_time_in_zones(df, ftp)
    return sanitize_dict({**summary, **zones})

def process_latest_fit_file(access_token):
    dbx = dropbox.Dropbox(access_token)
    dbx_path = get_latest_dropbox_file_path(dbx, DROPBOX_FOLDER)
    metadata, res = dbx.files_download(dbx_path)
    data = parse_fit_file(res.content)

    # Save to DB
    save_ride_summary(data)
    return data
