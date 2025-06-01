# scripts/trend_analysis.py

from scripts.ride_database import get_all_rides
import pandas as pd
from datetime import timedelta

def calculate_trend_metrics():
    # Get all rides from Postgres
    rides = get_all_rides()
    
    if not rides:
        return {"message": "No ride data available yet."}

    # Create a DataFrame from ride data
    data = []
    for ride in rides:
        data.append({
            "ride_id": ride.ride_id,
            "start_time": ride.start_time,
            "tss": ride.tss or 0
        })

    df = pd.DataFrame(data)
    df = df.sort_values("start_time")
    df.set_index("start_time", inplace=True)

    # Resample daily TSS, filling gaps with 0
    daily_tss = df["tss"].resample("D").sum().fillna(0)

    # Calculate 7-day rolling average (ATL) and 42-day rolling average (CTL)
    atl = daily_tss.rolling(window=7).mean().fillna(0)
    ctl = daily_tss.rolling(window=42).mean().fillna(0)

    # Calculate TSB (CTL - ATL)
    tsb = ctl - atl

    # Last day metrics (most recent trend state)
    latest_date = daily_tss.index.max()
    latest_ctl = ctl.loc[latest_date]
    latest_atl = atl.loc[latest_date]
    latest_tsb = tsb.loc[latest_date]

    # Format output
    trend_data = {
        "latest_date": latest_date.strftime("%Y-%m-%d"),
        "CTL": round(latest_ctl, 2),
        "ATL": round(latest_atl, 2),
        "TSB": round(latest_tsb, 2),
        "7_day_load": round(daily_tss[-7:].sum(), 2),
        "42_day_load": round(daily_tss[-42:].sum(), 2)
    }

    return trend_data
