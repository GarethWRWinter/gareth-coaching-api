import os
import logging
from dotenv import load_dotenv
from scripts.dropbox_utils import download_latest_fit_file
from scripts.parse_fit import parse_fit_to_dataframe
from scripts.calculate_tss import calculate_tss
from scripts.time_in_zones import calculate_time_in_zones
from scripts.sanitize import sanitize
from scripts.dropbox_auth import refresh_dropbox_token

load_dotenv()

DROPBOX_FOLDER = os.getenv("DROPBOX_FOLDER", "/Apps/WahooFitness")
FTP = int(os.getenv("FTP", 250))  # Default fallback FTP
logger = logging.getLogger(__name__)

def process_latest_fit_file(access_token: str) -> dict:
    try:
        # Step 1: Download latest FIT file from Dropbox
        fit_path = download_latest_fit_file(access_token)

        # Step 2: Parse FIT file to DataFrame
        df = parse_fit_to_dataframe(fit_path)
        if df.empty or "power" not in df.columns:
            raise ValueError("Parsed FIT file has no power data.")

        # Step 3: Compute metrics
        tss, np, intensity = calculate_tss(df["power"].values, FTP)
        time_in_zones = calculate_time_in_zones(df["power"].values, FTP)

        # Step 4: Create summary
        summary = {
            "ride_id": os.path.basename(fit_path).replace(".fit", ""),
            "start_time": df["timestamp"].iloc[0] if "timestamp" in df else None,
            "duration_sec": int(df["timestamp"].iloc[-1] - df["timestamp"].iloc[0]).total_seconds() if "timestamp" in df else len(df),
            "tss": round(tss, 2),
            "np": round(np, 2),
            "intensity": round(intensity, 3),
            "avg_power": round(df["power"].mean(), 2),
            "max_power": int(df["power"].max()),
            "avg_hr": round(df["heart_rate"].mean(), 2) if "heart_rate" in df else None,
            "avg_cadence": round(df["cadence"].mean(), 2) if "cadence" in df else None,
            "time_in_zones": time_in_zones,
        }

        # Step 5: Sanitize and return
        return sanitize(summary)

    except Exception as e:
        logger.exception("Error processing latest FIT file")
        raise RuntimeError("Failed to process latest FIT file") from e
