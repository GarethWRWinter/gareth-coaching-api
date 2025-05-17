# scripts/sanitize.py

import pandas as pd
import numpy as np

def sanitize_fit_data(df: pd.DataFrame) -> pd.DataFrame:
    if not isinstance(df, pd.DataFrame):
        return pd.DataFrame()

    df = df.copy()

    # Drop rows with missing timestamps (essential for time-series)
    df = df.dropna(subset=["timestamp"])

    # Ensure consistent dtypes for serialization
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    for col in df.select_dtypes(include=["float64", "int64"]).columns:
        df[col] = df[col].astype(float)

    # Replace NaNs with None (for JSON)
    df = df.where(pd.notnull(df), None)

    return df
