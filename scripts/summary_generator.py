
import pandas as pd

def generate_summary(data: pd.DataFrame) -> dict:
    summary = {
        "duration_sec": int((data["timestamp"].iloc[-1] - data["timestamp"].iloc[0]).total_seconds()),
        "avg_power": round(data["power"].mean(), 1),
        "max_power": int(data["power"].max()),
        "avg_hr": round(data["heart_rate"].mean(), 1) if "heart_rate" in data else None,
        "max_hr": int(data["heart_rate"].max()) if "heart_rate" in data else None,
        "avg_cadence": round(data["cadence"].mean(), 1) if "cadence" in data else None,
        "max_cadence": int(data["cadence"].max()) if "cadence" in data else None,
        "distance_km": round(data["distance"].iloc[-1] / 1000, 2) if "distance" in data else None,
        "total_work_kj": round(data["power"].sum() * data.shape[0] / 1000 / 60, 2),  # in kJ
        "time_in_zones": get_time_in_zones(data["power"]),
    }
    return summary

def get_time_in_zones(power_series: pd.Series) -> dict:
    zones = {
        "Z1 (<55%)": 0,
        "Z2 (56–75%)": 0,
        "Z3 (76–90%)": 0,
        "Z4 (91–105%)": 0,
        "Z5 (106–120%)": 0,
        "Z6 (121–150%)": 0,
        "Z7 (150%+)": 0,
    }
    ftp = 308  # Gareth's FTP

    for p in power_series:
        if p < 0.55 * ftp:
            zones["Z1 (<55%)"] += 1
        elif p <= 0.75 * ftp:
            zones["Z2 (56–75%)"] += 1
        elif p <= 0.90 * ftp:
            zones["Z3 (76–90%)"] += 1
        elif p <= 1.05 * ftp:
            zones["Z4 (91–105%)"] += 1
        elif p <= 1.20 * ftp:
            zones["Z5 (106–120%)"] += 1
        elif p <= 1.50 * ftp:
            zones["Z6 (121–150%)"] += 1
        else:
            zones["Z7 (150%+)"] += 1

    return {
        zone: {
            "seconds": seconds,
            "minutes": round(seconds / 60, 2)
        } for zone, seconds in zones.items()
    }
