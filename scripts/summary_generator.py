
import pandas as pd
from datetime import datetime

def generate_ride_summary(data: list[dict]) -> dict:
    df = pd.DataFrame(data)

    if df.empty:
        raise ValueError("No ride data to summarize.")

    # Ensure numeric
    for col in ['power', 'heart_rate', 'cadence', 'distance']:
        df[col] = pd.to_numeric(df.get(col, 0), errors='coerce').fillna(0)

    # Duration = number of data points (assuming 1Hz recording)
    duration_sec = len(df)

    # Distance in km
    distance_km = round(df['distance'].max() / 1000, 2) if 'distance' in df else 0

    # Work in kJ
    total_work_kj = round(df['power'].sum() / 1000, 2)

    # Date from first timestamp
    if 'timestamp' in df.columns and not df['timestamp'].isna().all():
        first_ts = df['timestamp'].dropna().iloc[0]
        ride_date = str(pd.to_datetime(first_ts).date())
    else:
        ride_date = str(datetime.utcnow().date())

    # Time in power zones (based on 308W FTP)
    ftp = 308
    zones = {
        'Z1': (0, 0.55 * ftp),
        'Z2': (0.56 * ftp, 0.75 * ftp),
        'Z3': (0.76 * ftp, 0.90 * ftp),
        'Z4': (0.91 * ftp, 1.05 * ftp),
        'Z5': (1.06 * ftp, 1.20 * ftp),
        'Z6': (1.21 * ftp, 1.50 * ftp),
        'Z7': (1.51 * ftp, 2000),
    }
    time_in_zones = {
        z: int(((df['power'] >= rng[0]) & (df['power'] <= rng[1])).sum())
        for z, rng in zones.items()
    }

    summary_dict = {
        "date": ride_date,
        "duration_sec": duration_sec,
        "avg_hr": round(df['heart_rate'].mean(), 1),
        "max_hr": int(df['heart_rate'].max()),
        "avg_power": round(df['power'].mean(), 1),
        "max_power": int(df['power'].max()),
        "avg_cadence": round(df['cadence'].mean(), 1),
        "max_cadence": int(df['cadence'].max()),
        "distance_km": distance_km,
        "total_work_kj": total_work_kj,
        "time_in_zones": time_in_zones
    }

    return summary_dict
