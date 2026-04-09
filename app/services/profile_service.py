"""Rider strengths/weaknesses profiling."""

from sqlalchemy.orm import Session

from app.core.formulas import rider_profile_scores, rider_type_profile, w_per_kg
from app.models.user import User
from app.services.metrics_service import get_all_time_power_profile, get_current_fitness, get_recent_power_profile


def get_fitness_summary(db: Session, user: User, include_power_profile: bool = True) -> dict:
    """Build a comprehensive fitness summary for the rider."""
    fitness = get_current_fitness(db, user.id)

    # Use 90-day power profile for current form (rider type, profile scores).
    # Skip it entirely when called with include_power_profile=False (fast dashboard load).
    power_profile_raw = {}
    if include_power_profile:
        try:
            power_profile_raw = get_recent_power_profile(db, user.id, days=90)
        except Exception:
            power_profile_raw = {}

    # Extract just power values for existing functions (new format includes ride_id/date)
    power_values = {d: v["best_power"] for d, v in power_profile_raw.items()}

    ftp = user.ftp or 0
    weight = user.weight_kg or 0

    # Rider type profiling
    profile = {"type": "unknown", "strengths": [], "weaknesses": []}
    if ftp > 0 and weight > 0:
        profile = rider_type_profile(power_values, ftp, weight)

    # Radar chart scores (0-100 per energy system)
    profile_scores = {}
    if weight > 0:
        profile_scores = rider_profile_scores(power_values, weight)

    # Fitness level classification based on CTL
    ctl = fitness["ctl"]
    if ctl < 20:
        fitness_level = "untrained"
    elif ctl < 40:
        fitness_level = "fair"
    elif ctl < 60:
        fitness_level = "moderate"
    elif ctl < 80:
        fitness_level = "good"
    elif ctl < 100:
        fitness_level = "very_good"
    else:
        fitness_level = "excellent"

    return {
        "ftp": ftp or None,
        "w_per_kg": w_per_kg(ftp, weight) if ftp and weight else None,
        "current_ctl": fitness["ctl"],
        "current_atl": fitness["atl"],
        "current_tsb": fitness["tsb"],
        "ramp_rate": fitness["ramp_rate"],
        "rider_type": profile["type"],
        "strengths": profile["strengths"],
        "weaknesses": profile["weaknesses"],
        "fitness_level": fitness_level,
        "profile_scores": profile_scores,
    }
