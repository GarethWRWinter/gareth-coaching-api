import pandas as pd
from scripts.ride_database import load_all_rides

def generate_trend_analysis():
    rides = load_all_rides()
    if not rides:
        return {"message": "No ride data available for trend analysis."}

    df = pd.DataFrame(rides)

    if "date" not in df.columns:
        df["date"] = pd.to_datetime(df["start_time"]).dt.date

    df["TSS"] = pd.to_numeric(df.get("TSS", 0), errors="coerce").fillna(0)

    df.sort_values("date", inplace=True)

    # Compute 7-day rolling load
    df["7_day_TSS"] = df["TSS"].rolling(window=7, min_periods=1).sum()

    # Aggregate zone times if available
    zone_cols = [col for col in df.columns if col.startswith("zone_")]
    zone_summary = {}
    for col in zone_cols:
        total_seconds = df[col].sum()
        zone_summary[col] = {
            "minutes": round(total_seconds / 60, 1),
            "hours": round(total_seconds / 3600, 2)
        }

    return {
        "rides_analyzed": len(df),
        "7_day_TSS": df["7_day_TSS"].iloc[-1],
        "TSS_total": df["TSS"].sum(),
        "zone_time_summary": zone_summary
    }
