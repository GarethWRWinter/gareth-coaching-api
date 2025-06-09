# scripts/ride_processor.py

import pandas as pd
from scripts.fit_metrics import calculate_ride_metrics

def process_ride_data(df: pd.DataFrame) -> Dict:
    """
    Process and compute all ride metrics, returning a complete dictionary.
    """
    # Calculate all metrics
    ride_metrics = calculate_ride_metrics(df)
    
    return ride_metrics
