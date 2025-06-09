# scripts/ride_processor.py

import pandas as pd
from scripts.fit_metrics import calculate_ride_metrics

def process_ride_data(df: pd.DataFrame, ftp: float) -> Dict:
    """
    Process and compute all ride metrics, returning a complete dictionary.
    Args:
        df: Ride data as Pandas DataFrame.
        ftp: Current FTP in watts.
    """
    # Calculate all metrics using the dynamic FTP-based zones
    ride_metrics = calculate_ride_metrics(df, ftp)
    return ride_metrics
