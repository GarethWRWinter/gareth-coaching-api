"""Race day projection service — BestBikeSplit-inspired performance estimation.

Calculates:
- Estimated finish time based on rider FTP, weight, and course elevation profile
- Segment-by-segment pacing strategy with power targets and zone assignments
- Fitness trajectory projection (CTL/FTP growth from now to event day)
- Performance comparison: "You Today" vs "You on Race Day"
"""

import math
from datetime import date, timedelta

from app.core.constants import POWER_ZONES

# ---------------------------------------------------------------------------
# Physics defaults
# ---------------------------------------------------------------------------
DEFAULT_CDA = 0.35        # Drag area (m²) — road bike, hoods position
DEFAULT_CRR = 0.005       # Rolling resistance coefficient — typical road tire
DEFAULT_RHO = 1.225       # Air density (kg/m³) at sea level, 15°C
GRAVITY = 9.81            # m/s²
MIN_SPEED_KPH = 5.0       # Walking pace (steep climb)
MAX_SPEED_KPH = 80.0      # Safety cap on descents


# ---------------------------------------------------------------------------
# A. Physics model — speed from power
# ---------------------------------------------------------------------------

def speed_from_power(
    power_watts: float,
    weight_kg: float,
    gradient_pct: float,
    cda: float = DEFAULT_CDA,
    crr: float = DEFAULT_CRR,
    rho: float = DEFAULT_RHO,
) -> float:
    """
    Solve for cycling speed (m/s) given power, weight, and gradient.

    Uses Newton's method on:
        P = (m·g·sin(θ) + Crr·m·g·cos(θ))·v + 0.5·CdA·ρ·v³

    Returns speed in m/s, clamped to [MIN_SPEED, MAX_SPEED].
    """
    grade = gradient_pct / 100.0
    theta = math.atan(grade)
    sin_t = math.sin(theta)
    cos_t = math.cos(theta)

    # Linear resistance term: gravity + rolling
    linear_coeff = weight_kg * GRAVITY * (sin_t + crr * cos_t)
    # Cubic aero term coefficient
    cubic_coeff = 0.5 * cda * rho

    # Newton's method — solve f(v) = cubic_coeff·v³ + linear_coeff·v - P = 0
    v = 8.0  # initial guess (m/s ≈ 29 km/h)

    for _ in range(50):
        f = cubic_coeff * v**3 + linear_coeff * v - power_watts
        f_prime = 3.0 * cubic_coeff * v**2 + linear_coeff

        if abs(f_prime) < 1e-12:
            break

        v_new = v - f / f_prime
        v_new = max(v_new, MIN_SPEED_KPH / 3.6)  # clamp minimum

        if abs(v_new - v) < 1e-6:
            break
        v = v_new

    # Clamp to reasonable range
    v = max(v, MIN_SPEED_KPH / 3.6)
    v = min(v, MAX_SPEED_KPH / 3.6)

    return v


# ---------------------------------------------------------------------------
# B. Pacing strategy
# ---------------------------------------------------------------------------

def _sustainability_factor(event_duration_hours: float) -> float:
    """Fraction of FTP sustainable for event duration."""
    if event_duration_hours <= 1.0:
        return 0.95
    elif event_duration_hours <= 1.5:
        return 0.90
    elif event_duration_hours <= 2.5:
        return 0.85
    elif event_duration_hours <= 4.0:
        return 0.80
    elif event_duration_hours <= 6.0:
        return 0.75
    else:
        return 0.70


def _gradient_power_multiplier(gradient_pct: float) -> float:
    """Adjust target power based on gradient (BestBikeSplit-style)."""
    if gradient_pct > 8.0:
        return 1.12   # Push hard on steep climbs — speed matters most
    elif gradient_pct > 4.0:
        return 1.08
    elif gradient_pct > 1.5:
        return 1.03
    elif gradient_pct > -1.5:
        return 1.00   # Flat — base effort
    elif gradient_pct > -4.0:
        return 0.85   # Gentle descent — soft pedal
    else:
        return 0.55   # Steep descent — coast, gravity does the work


def _power_to_zone(power_watts: float, ftp: float) -> tuple[str, str]:
    """Determine power zone for a given power and FTP."""
    pct = power_watts / ftp if ftp > 0 else 0

    for zone_key in ["Z7", "Z6", "Z5", "Z4", "Z3", "Z2", "Z1"]:
        zone = POWER_ZONES[zone_key]
        if pct >= zone["low"]:
            return zone_key, zone["name"]

    return "Z1", POWER_ZONES["Z1"]["name"]


def calculate_pacing(
    ftp: int,
    weight_kg: float,
    elevation_profile: list[dict],
    event_duration_hours: float = 3.0,
) -> dict:
    """
    Calculate segment-by-segment pacing strategy and estimated finish time.

    Args:
        ftp: Functional threshold power (watts)
        weight_kg: Rider weight (kg)
        elevation_profile: List of {distance_km, elevation_m, gradient_pct}
        event_duration_hours: Expected event duration for sustainability calc

    Returns:
        dict with "segments", "total_time_seconds", "avg_power_watts", "avg_speed_kph"
    """
    if not elevation_profile or len(elevation_profile) < 2:
        return {
            "segments": [],
            "total_time_seconds": 0,
            "avg_power_watts": 0,
            "avg_speed_kph": 0.0,
        }

    sustainability = _sustainability_factor(event_duration_hours)
    base_power = ftp * sustainability

    segments = []
    total_time_seconds = 0
    total_distance_km = 0
    power_time_sum = 0  # for weighted average power

    for i in range(1, len(elevation_profile)):
        prev = elevation_profile[i - 1]
        curr = elevation_profile[i]

        seg_distance_km = curr["distance_km"] - prev["distance_km"]
        if seg_distance_km <= 0:
            continue

        seg_distance_m = seg_distance_km * 1000
        gradient = curr.get("gradient_pct", 0) or 0

        # Calculate target power
        multiplier = _gradient_power_multiplier(gradient)
        target_power = base_power * multiplier

        # Cap at FTP × 1.05 (sustainable for event-length efforts)
        target_power = min(target_power, ftp * 1.05)
        # Floor at 80W (coasting/descents still involve some pedalling)
        target_power = max(target_power, 80)

        # Calculate speed
        speed_ms = speed_from_power(target_power, weight_kg, gradient)
        speed_kph = speed_ms * 3.6

        # Calculate time
        seg_time_seconds = seg_distance_m / speed_ms if speed_ms > 0 else 0

        # Zone
        zone_key, zone_name = _power_to_zone(target_power, ftp)

        total_time_seconds += seg_time_seconds
        total_distance_km += seg_distance_km
        power_time_sum += target_power * seg_time_seconds

        segments.append({
            "distance_km": round(curr["distance_km"], 2),
            "elevation_m": round(curr["elevation_m"], 1),
            "gradient_pct": round(gradient, 1),
            "target_power_watts": round(target_power),
            "target_power_pct_ftp": round((target_power / ftp) * 100) if ftp else 0,
            "estimated_speed_kph": round(speed_kph, 1),
            "zone": zone_key,
            "zone_name": zone_name,
        })

    avg_power = round(power_time_sum / total_time_seconds) if total_time_seconds > 0 else 0
    avg_speed = round((total_distance_km / (total_time_seconds / 3600)), 1) if total_time_seconds > 0 else 0

    return {
        "segments": segments,
        "total_time_seconds": round(total_time_seconds),
        "avg_power_watts": avg_power,
        "avg_speed_kph": avg_speed,
    }


# ---------------------------------------------------------------------------
# C. Fitness / FTP projection
# ---------------------------------------------------------------------------

def _ftp_growth_factor(experience_level: str | None) -> float:
    """How much FTP tracks CTL growth, by experience level."""
    factors = {
        "beginner": 0.12,
        "intermediate": 0.08,
        "advanced": 0.05,
        "elite": 0.03,
    }
    return factors.get(experience_level or "intermediate", 0.08)


def project_fitness(
    current_ctl: float,
    current_ftp: int,
    days_until: int,
    experience_level: str | None = None,
    weekly_tss_target: float | None = None,
) -> list[dict]:
    """
    Project CTL and FTP from today to event day.

    FTP tracks peak CTL (pre-taper) — the taper phase preserves FTP while
    restoring freshness. This prevents the common error of showing FTP
    declining during a taper.

    Returns sampled trajectory points (every 3-7 days) with milestone labels.
    """
    if days_until <= 0:
        return [{
            "date": date.today().isoformat(),
            "ctl": round(current_ctl, 1),
            "ftp": current_ftp,
            "label": "Today / Race Day",
        }]

    # Determine daily TSS assumption
    if weekly_tss_target and weekly_tss_target > 0:
        daily_tss = weekly_tss_target / 7.0
    else:
        # Conservative assumption: daily TSS ≈ current CTL × 1.2
        # (progressive overload — need to exceed current load to grow)
        daily_tss = max(current_ctl * 1.2, 50)

    # Taper parameters
    taper_start_day = max(0, days_until - 14)  # 2 weeks of taper
    taper_tss_factor = 0.50  # 50% volume during taper

    # CTL decay constant (from formulas.py pattern)
    tc = 42
    decay_factor = 1 - math.exp(-1 / tc)

    # Simulate day by day
    ctl = current_ctl
    growth_factor = _ftp_growth_factor(experience_level)
    baseline_ctl = current_ctl

    # Track peak CTL (pre-taper) for FTP calculation
    peak_ctl = current_ctl

    trajectory_points = []
    today = date.today()

    # Determine sample interval based on plan length
    if days_until <= 14:
        sample_interval = 1
    elif days_until <= 30:
        sample_interval = 2
    elif days_until <= 60:
        sample_interval = 3
    else:
        sample_interval = 5

    for day in range(days_until + 1):
        current_date = today + timedelta(days=day)

        # Determine daily TSS
        if day >= taper_start_day and taper_start_day > 0:
            tss = daily_tss * taper_tss_factor
        else:
            # Gentle progressive overload: +0.5% per week
            weekly_bump = 1.0 + (day / 7) * 0.005
            tss = daily_tss * weekly_bump

        # Update CTL
        ctl = ctl + (tss - ctl) * decay_factor

        # Track peak CTL (before taper kicks in)
        if ctl > peak_ctl:
            peak_ctl = ctl

        # FTP tracks PEAK CTL growth, not current CTL
        # (taper reduces CTL for freshness but doesn't lose FTP in 2 weeks)
        peak_ctl_gain_pct = (peak_ctl - baseline_ctl) / max(baseline_ctl, 1)
        ftp = current_ftp * (1 + peak_ctl_gain_pct * growth_factor)

        # Sample this point?
        is_first = day == 0
        is_last = day == days_until
        is_taper_start = day == taper_start_day and taper_start_day > 0
        is_sample = day % sample_interval == 0

        if is_first or is_last or is_taper_start or is_sample:
            label = None
            if is_first:
                label = "Today"
            elif is_last:
                label = "Race Day"
            elif is_taper_start:
                label = "Taper Starts"

            trajectory_points.append({
                "date": current_date.isoformat(),
                "ctl": round(ctl, 1),
                "ftp": round(ftp),
                "label": label,
            })

    return trajectory_points


# ---------------------------------------------------------------------------
# D. Main projection function
# ---------------------------------------------------------------------------

def get_race_projection(
    goal,
    user,
    db,
) -> dict | None:
    """
    Build complete race projection for a goal event.

    Requires: user.ftp, user.weight_kg, goal.route_data.elevation_profile

    Returns dict matching RaceProjectionResponse schema, or None if data insufficient.
    """
    from app.services.metrics_service import get_current_fitness

    # Validate required data
    if not user.ftp or not user.weight_kg or user.weight_kg <= 0:
        return None

    route_data = goal.route_data
    if not route_data or not route_data.get("elevation_profile"):
        return None

    elevation_profile = route_data["elevation_profile"]
    if len(elevation_profile) < 2:
        return None

    # Get current fitness
    try:
        fitness = get_current_fitness(db, user.id)
        current_ctl = fitness.get("ctl", 0)
    except Exception:
        current_ctl = 0

    # Days until event
    today = date.today()
    event_date = goal.event_date
    if hasattr(event_date, "date") and callable(getattr(event_date, "date", None)):
        event_date = event_date.date()
    days_until = (event_date - today).days

    # Estimate event duration for sustainability factor
    if goal.target_duration_minutes:
        event_duration_hours = goal.target_duration_minutes / 60.0
    else:
        # Rough estimate: 30 km/h average on a road bike
        total_distance = route_data.get("total_distance_km", 80)
        event_duration_hours = total_distance / 28.0  # slightly conservative

    # === Current performance ===
    current_pacing = calculate_pacing(
        ftp=user.ftp,
        weight_kg=user.weight_kg,
        elevation_profile=elevation_profile,
        event_duration_hours=event_duration_hours,
    )

    current_performance = {
        "estimated_time_seconds": current_pacing["total_time_seconds"],
        "avg_power_watts": current_pacing["avg_power_watts"],
        "avg_speed_kph": current_pacing["avg_speed_kph"],
        "ftp_used": user.ftp,
        "ctl_used": round(current_ctl, 1),
    }

    # === Projected performance (only if event > 7 days away) ===
    projected_performance = None
    improvement = None

    if days_until > 7:
        # Get average weekly TSS from training plan if one exists
        weekly_tss = _get_weekly_tss_from_plan(goal, db)

        trajectory = project_fitness(
            current_ctl=current_ctl,
            current_ftp=user.ftp,
            days_until=days_until,
            experience_level=(
                user.experience_level.value
                if hasattr(user.experience_level, "value")
                else user.experience_level
            ) if user.experience_level else None,
            weekly_tss_target=weekly_tss,
        )

        if trajectory:
            race_day_point = trajectory[-1]
            projected_ftp = race_day_point["ftp"]
            projected_ctl = race_day_point["ctl"]

            # Recalculate pacing with projected FTP
            projected_pacing = calculate_pacing(
                ftp=projected_ftp,
                weight_kg=user.weight_kg,
                elevation_profile=elevation_profile,
                event_duration_hours=event_duration_hours,
            )

            projected_performance = {
                "estimated_time_seconds": projected_pacing["total_time_seconds"],
                "avg_power_watts": projected_pacing["avg_power_watts"],
                "avg_speed_kph": projected_pacing["avg_speed_kph"],
                "ftp_used": projected_ftp,
                "ctl_used": projected_ctl,
            }

            time_saved = current_pacing["total_time_seconds"] - projected_pacing["total_time_seconds"]
            speed_gain = projected_pacing["avg_speed_kph"] - current_pacing["avg_speed_kph"]
            ftp_gain = projected_ftp - user.ftp

            improvement = {
                "time_saved_seconds": max(0, round(time_saved)),
                "speed_gain_kph": round(max(0, speed_gain), 1),
                "ftp_gain_watts": max(0, round(ftp_gain)),
            }
    else:
        # Event is soon — just build a short trajectory for visual
        trajectory = project_fitness(
            current_ctl=current_ctl,
            current_ftp=user.ftp,
            days_until=max(days_until, 0),
            experience_level=(
                user.experience_level.value
                if hasattr(user.experience_level, "value")
                else user.experience_level
            ) if user.experience_level else None,
        )

    return {
        "current_performance": current_performance,
        "projected_performance": projected_performance,
        "improvement": improvement,
        "pacing_strategy": current_pacing["segments"],
        "fitness_trajectory": trajectory,
    }


def _get_weekly_tss_from_plan(goal, db) -> float | None:
    """Try to get average weekly TSS from an active training plan linked to this goal."""
    try:
        from app.models.training import TrainingPlan, TrainingPhase

        plan = (
            db.query(TrainingPlan)
            .filter(
                TrainingPlan.goal_event_id == goal.id,
                TrainingPlan.status == "active",
            )
            .first()
        )
        if not plan:
            return None

        phases = (
            db.query(TrainingPhase)
            .filter(TrainingPhase.plan_id == plan.id)
            .all()
        )
        if not phases:
            return None

        # Average the target weekly TSS across build/peak phases
        tss_values = [
            p.target_weekly_tss
            for p in phases
            if p.target_weekly_tss and p.phase_type in ("build", "peak", "base")
        ]
        return sum(tss_values) / len(tss_values) if tss_values else None

    except Exception:
        return None
