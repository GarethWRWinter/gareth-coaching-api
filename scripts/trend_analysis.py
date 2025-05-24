# scripts/trend_analysis.py

from datetime import datetime
import pandas as pd
from scripts.ride_database import load_all_rides

def compute_trend_metrics():
    rides = load_all_rides()
    if not rides:
        return {"error": "No ride data found."}

    df = pd.DataFrame(rides)

    # Parse and clean timestamps
    df['date'] = pd.to_datetime(df['start_time'], errors='coerce')
    df = df.dropna(subset=['date'])
    df['date'] = df['date'].dt.date
    df = df.sort_values(by='date')

    # Convert TSS to float, fill missing with 0
    df['TSS'] = pd.to_numeric(df.get('tss', 0), errors='coerce').fillna(0)
    df['date'] = pd.to_datetime(df['date'])

    if df.empty or df['TSS'].sum() == 0:
        return {"error": "Insufficient ride data to compute trends."}

    # Compute rolling metrics
    df.set_index('date', inplace=True)
    daily_tss = df.resample('D').sum()['TSS'].fillna(0)
    ctl = daily_tss.rolling(window=42).mean()
    atl = daily_tss.rolling(window=7).mean()
    tsb = ctl - atl

    today = daily_tss.index.max()

    trend = {
        "7_day_tss_avg": round(daily_tss[-7:].mean(), 2),
        "28_day_tss_avg": round(daily_tss[-28:].mean(), 2),
        "CTL": round(ctl[-1], 2) if not ctl.empty else None,
        "ATL": round(atl[-1], 2) if not atl.empty else None,
        "TSB": round(tsb[-1], 2) if not tsb.empty else None,
        "last_updated": str(today.date()) if pd.notna(today) else None,
    }

    # Interpret status flag from TSB (Training Stress Balance)
    if trend["TSB"] is None:
        trend["status_flag"] = "Unknown"
    elif trend["TSB"] < -10:
        trend["status_flag"] = "Overreaching"
    elif trend["TSB"] > 10:
        trend["status_flag"] = "Fresh"
    else:
        trend["status_flag"] = "Neutral"

    # FTP tracking (if available)
    try:
        df['ftp'] = pd.to_numeric(df['ftp'], errors='coerce')
        trend["FTP"] = int(df['ftp'].dropna().iloc[-1])
    except:
        trend["FTP"] = "Unknown"

    return trend
