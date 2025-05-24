# scripts/trend_analysis.py

from datetime import datetime, timedelta
import pandas as pd
from scripts.ride_database import load_all_rides

def compute_trend_metrics():
    rides = load_all_rides()
    if not rides:
        return {"error": "No ride data found."}

    df = pd.DataFrame(rides)
    df['date'] = pd.to_datetime(df['start_time']).dt.date
    df = df.sort_values(by='date')

    df['TSS'] = pd.to_numeric(df['tss'], errors='coerce').fillna(0)
    df['date'] = pd.to_datetime(df['date'])

    today = df['date'].max()
    df['days_since'] = (today - df['date']).dt.days

    # CTL = 42-day rolling avg, ATL = 7-day avg
    df.set_index('date', inplace=True)
    daily_tss = df.resample('D').sum()['TSS'].fillna(0)
    ctl = daily_tss.rolling(window=42).mean()
    atl = daily_tss.rolling(window=7).mean()
    tsb = ctl - atl

    trend = {
        "7_day_tss_avg": round(daily_tss[-7:].mean(), 2),
        "28_day_tss_avg": round(daily_tss[-28:].mean(), 2),
        "CTL": round(ctl[-1], 2),
        "ATL": round(atl[-1], 2),
        "TSB": round(tsb[-1], 2),
        "last_updated": str(today)
    }

    if trend["TSB"] < -10:
        trend["status_flag"] = "Overreaching"
    elif trend["TSB"] > 10:
        trend["status_flag"] = "Fresh"
    else:
        trend["status_flag"] = "Neutral"

    try:
        trend["FTP"] = int(df['ftp'].dropna().iloc[-1])
    except:
        trend["FTP"] = "Unknown"

    return trend
