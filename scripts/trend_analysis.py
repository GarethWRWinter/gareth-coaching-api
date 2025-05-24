from datetime import datetime
import pandas as pd
from scripts.ride_database import get_all_rides

def compute_trend_metrics():
    rides = get_all_rides()
    if not rides:
        return {"message": "No ride data available for trend analysis."}

    df = pd.DataFrame(rides)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values(by='date')

    df['TSS'] = pd.to_numeric(df['tss'], errors='coerce').fillna(0)
    df.set_index('date', inplace=True)

    daily_tss = df['TSS'].resample('D').sum().fillna(0)
    ctl = daily_tss.rolling(window=42).mean()
    atl = daily_tss.rolling(window=7).mean()
    tsb = ctl - atl

    trend = {
        "7_day_tss_avg": round(daily_tss[-7:].mean(), 2),
        "28_day_tss_avg": round(daily_tss[-28:].mean(), 2),
        "CTL": round(ctl[-1], 2),
        "ATL": round(atl[-1], 2),
        "TSB": round(tsb[-1], 2),
        "last_updated": str(df.index.max().date())
    }

    tsb_value = trend["TSB"]
    if tsb_value < -10:
        trend["status_flag"] = "Overreaching"
    elif tsb_value > 10:
        trend["status_flag"] = "Fresh"
    else:
        trend["status_flag"] = "Neutral"

    return trend
