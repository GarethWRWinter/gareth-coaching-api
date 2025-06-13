import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime, timedelta
import os

DATABASE_URL = os.getenv("DATABASE_URL")

def get_trend_analysis():
    try:
        engine = create_engine(DATABASE_URL)
        query = "SELECT * FROM rides ORDER BY start_time ASC"
        df = pd.read_sql(query, engine)

        if df.empty:
            return {
                "latest_date": None,
                "CTL": 0,
                "ATL": 0,
                "TSB": 0,
                "7_day_load": 0,
                "42_day_load": 0,
            }

        df['start_time'] = pd.to_datetime(df['start_time'])
        df['tss'] = pd.to_numeric(df['tss'], errors='coerce').fillna(0)

        df = df.sort_values(by="start_time")
        df.set_index("start_time", inplace=True)

        today = datetime.now().date()
        ts_range = pd.date_range(end=today, periods=42)

        tss_series = df['tss'].resample("D").sum().reindex(ts_range, fill_value=0)

        # CTL: 42-day exponential moving average with time constant 42
        ctl = tss_series.ewm(span=42, adjust=False).mean().iloc[-1]
        # ATL: 7-day exponential moving average
        atl = tss_series.ewm(span=7, adjust=False).mean().iloc[-1]
        tsb = ctl - atl

        # Load summaries
        load_7 = tss_series[-7:].sum()
        load_42 = tss_series.sum()

        return {
            "latest_date": str(ts_range[-1].date()),
            "CTL": round(ctl, 1),
            "ATL": round(atl, 1),
            "TSB": round(tsb, 1),
            "7_day_load": round(load_7, 1),
            "42_day_load": round(load_42, 1),
        }

    except Exception as e:
        raise RuntimeError(f"Trend analysis failed: {str(e)}")
