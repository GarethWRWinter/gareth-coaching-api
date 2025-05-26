from scripts.ride_database import get_all_rides as load_all_rides

def compute_trend_metrics():
    rides = load_all_rides()
    if not rides:
        return {"message": "No ride data available for trend analysis."}

    valid_rides = [ride for ride in rides if isinstance(ride.get("tss"), (int, float))]
    if not valid_rides:
        return {"message": "No valid TSS data found for trend analysis."}

    total_tss = sum(ride.get("tss", 0) or 0 for ride in valid_rides)
    average_tss = total_tss / len(valid_rides)

    ctl = average_tss * 0.9
    atl = average_tss * 1.1
    tsb = ctl - atl

    return {
        "total_rides": len(valid_rides),
        "average_tss": round(average_tss, 2),
        "weekly_load": round(total_tss, 2),
        "ctl": round(ctl, 2),
        "atl": round(atl, 2),
        "tsb": round(tsb, 2),
        "ftp_trend": "↗︎ Placeholder",  # Replace with real FTP tracking later
        "zone_focus": "Z2-heavy",       # Placeholder for time-in-zone trend analysis
    }
