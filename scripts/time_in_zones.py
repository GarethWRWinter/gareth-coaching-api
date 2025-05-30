def calculate_time_in_zones(df, ftp):
    # Ensure 'power' column is numeric
    df["power"] = pd.to_numeric(df["power"], errors="coerce")

    zones = {
        "Zone 1: Active Recovery": 0,
        "Zone 2: Endurance": 0,
        "Zone 3: Tempo": 0,
        "Zone 4: Threshold": 0,
        "Zone 5: VO2max": 0,
        "Zone 6: Anaerobic Capacity": 0,
        "Zone 7: Neuromuscular Power": 0,
    }

    for power in df["power"].dropna():
        if power < 0.55 * ftp:
            zones["Zone 1: Active Recovery"] += 1
        elif power < 0.75 * ftp:
            zones["Zone 2: Endurance"] += 1
        elif power < 0.90 * ftp:
            zones["Zone 3: Tempo"] += 1
        elif power < 1.05 * ftp:
            zones["Zone 4: Threshold"] += 1
        elif power < 1.20 * ftp:
            zones["Zone 5: VO2max"] += 1
        elif power < 1.50 * ftp:
            zones["Zone 6: Anaerobic Capacity"] += 1
        else:
            zones["Zone 7: Neuromuscular Power"] += 1

    total_seconds = sum(zones.values())
    zone_minutes = {zone: round(seconds / 60, 2) for zone, seconds in zones.items()}

    return {
        "seconds": zones,
        "minutes": zone_minutes,
        "total_seconds": total_seconds,
    }
