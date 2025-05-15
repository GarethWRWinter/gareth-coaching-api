import pandas as pd
from scripts.constants import POWER_ZONES

def generate_ride_summary(df: pd.DataFrame) -> dict:
    df['power'] = pd.to_numeric(df.get('power', 0), errors='coerce').fillna(0)
    df['heart_rate'] = pd.to_numeric(df.get('heart_rate', 0), errors='coerce').fillna(0)
    df['cadence'] = pd.to_numeric(df.get('cadence', 0), errors='coerce').fillna(0)
    df['distance'] = pd.to_numeric(df.get('distance', 0), errors='coerce').fillna(0)

    duration_sec = df.shape[0]
    total_work = df['power'].sum() * 1 / 1000  # kJ assuming 1s intervals
    distance_km = df['distance'].iloc[-1] / 1000 if not df['distance'].empty else 0

    time_in_zones = {zone['name']: 0 for zone in POWER_ZONES}
    for power in df['power']:
        for zone in POWER_ZONES:
            if zone['min'] <= power < zone['max']:
                time_in_zones[zone['name']] += 1
                break

    return {
        "date": str(df['timestamp'].iloc[0]) if 'timestamp' in df else None,
        "duration_sec": duration_sec,
        "avg_power": df['power'].mean(),
        "max_power": df['power'].max(),
        "avg_hr": df['heart_rate'].mean(),
        "max_hr": df['heart_rate'].max(),
        "avg_cadence": df['cadence'].mean(),
        "max_cadence": df['cadence'].max(),
        "distance_km": distance_km,
        "total_work_kj": total_work,
        "time_in_zones": time_in_zones
    }
