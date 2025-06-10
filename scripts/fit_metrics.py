import pandas as pd
from scripts.ride_database import get_ftp

def calculate_tss(ride_df: pd.DataFrame) -> float:
    """
    Calculate Training Stress Score (TSS) for a ride.
    Uses normalized power (NP), duration, FTP from DB.
    """
    np = ride_df["power"].mean()  # Simplified; replace with true NP calculation
    duration_hours = len(ride_df) / 3600
    ftp = get_ftp()

    intensity_factor = np / ftp if ftp else 0
    tss = (duration_hours * np * intensity_factor) / (ftp or 1) * 100
    return tss

def calculate_power_zones(ride_df: pd.DataFrame) -> dict:
    """
    Calculate time spent in each power zone dynamically based on FTP.
    """
    ftp = get_ftp()
    power_values = ride_df["power"]

    zones = {
        "Zone 1: Recovery": power_values[(power_values < 0.55 * ftp)].count(),
        "Zone 2: Endurance": power_values[(0.55 * ftp <= power_values) & (power_values < 0.75 * ftp)].count(),
        "Zone 3: Tempo": power_values[(0.75 * ftp <= power_values) & (power_values < 0.9 * ftp)].count(),
        "Zone 4: Threshold": power_values[(0.9 * ftp <= power_values) & (power_values < 1.05 * ftp)].count(),
        "Zone 5: VO2max": power_values[(1.05 * ftp <= power_values) & (power_values < 1.2 * ftp)].count(),
        "Zone 6: Anaerobic Capacity": power_values[(1.2 * ftp <= power_values) & (power_values < 1.5 * ftp)].count(),
        "Zone 7: Neuromuscular Power": power_values[(1.5 * ftp <= power_values)].count(),
    }

    return zones
