# scripts/ride_processor.py

import os
import pandas as pd
from scripts.parse_fit_to_df import parse_fit_to_dataframe
from scripts.fit_metrics import calculate_ride_metrics
from scripts.ride_database import save_ride_summary

def process_fit_file(fit_file_path, ftp):
    print(f"🔄 Processing FIT file: {fit_file_path}")

    df = parse_fit_to_dataframe(fit_file_path)

    if df is None or not isinstance(df, pd.DataFrame):
        raise ValueError("Parsed data is not a valid DataFrame.")
    if df.empty:
        raise ValueError("Parsed DataFrame is empty.")

    metrics = calculate_ride_metrics(df, ftp)
    save_ride_summary(metrics)
    return metrics
