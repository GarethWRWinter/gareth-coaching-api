import pandas as pd
from models.pydantic_models import RideSummary

def generate_ride_summary(data: list[dict]) -> RideSummary:
    df = pd.DataFrame(data)  # ✅ CONVERT list to DataFrame

    # Defensive guards
    if df.empty:
        raise ValueError("No ride data to summarize.")

    df['power'] = pd.to_numeric(df.get('power', 0), errors='coerce').fillna(0)
    df['heart_rate'] = pd.to_numeric(df.get('heart_rate', 0), errors='coerce').fillna(0)
    df['cadence'] = pd.to_numeric(df.get('cadence', 0), errors='coerce').fillna(0)

    summary = RideSummary(
        duration_seconds=len(df),
        avg_power=round(df['power'].mean(), 1),
        max_power=int(df['power'].max()),
        avg_heart_rate=round(df['heart_rate'].mean(), 1),
        max_heart_rate=int(df['heart_rate'].max()),
        avg_cadence=round(df['cadence'].mean(), 1),
        max_cadence=int(df['cadence'].max()),
    )

    return summary
