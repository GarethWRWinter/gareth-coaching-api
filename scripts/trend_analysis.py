from scripts.ride_database import load_all_rides


def generate_trend_analysis():
    rides = load_all_rides()
    if not rides:
        return {"message": "No ride data available for trend analysis."}

    # Example: Compute weekly TSS and CTL/ATL (stubbed)
    total_tss = sum(ride.get("tss", 0) for ride in rides)
    average_tss = total_tss / len(rides)

    return {
        "total_rides": len(rides),
        "average_tss": round(average_tss, 2),
        "weekly_load": total_tss,
        "ctl": round(average_tss * 0.9, 2),
        "atl": round(average_tss * 1.1, 2),
        "tsb": round(average_tss * (0.9 - 1.1), 2)
    }
