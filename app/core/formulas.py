"""Pure cycling math functions. Zero side effects, zero database/IO dependencies."""

import math

from app.core.constants import (
    ATL_TIME_CONSTANT,
    CTL_TIME_CONSTANT,
    FTP_FROM_20MIN_MULTIPLIER,
    HR_ZONES,
    NP_ROLLING_WINDOW,
    POWER_ZONES,
)


def normalized_power(power_samples: list[int | float], sample_rate_hz: int = 1) -> float:
    """
    Calculate Normalized Power (NP).

    1. Calculate 30-second rolling average of power
    2. Raise each average to the 4th power
    3. Take the mean of those values
    4. Take the 4th root

    Returns 0.0 if insufficient data (< 30 seconds).
    """
    window = NP_ROLLING_WINDOW * sample_rate_hz

    if len(power_samples) < window:
        return 0.0

    # Filter out None/negative values
    samples = [max(0, p) for p in power_samples if p is not None]
    if len(samples) < window:
        return 0.0

    # Calculate rolling averages
    rolling_avgs = []
    for i in range(len(samples) - window + 1):
        avg = sum(samples[i : i + window]) / window
        rolling_avgs.append(avg)

    if not rolling_avgs:
        return 0.0

    # Raise to 4th power, mean, then 4th root
    fourth_powers = [avg**4 for avg in rolling_avgs]
    mean_fourth = sum(fourth_powers) / len(fourth_powers)
    return mean_fourth**0.25


def intensity_factor(np: float, ftp: int) -> float:
    """IF = NP / FTP. Returns 0.0 if FTP is 0."""
    if ftp <= 0:
        return 0.0
    return np / ftp


def variability_index(np: float, avg_power: float) -> float:
    """VI = NP / Average Power. Returns 0.0 if avg_power is 0."""
    if avg_power <= 0:
        return 0.0
    return np / avg_power


def training_stress_score(
    duration_seconds: int, np: float, if_: float, ftp: int
) -> float:
    """
    TSS = (duration_seconds * NP * IF) / (FTP * 3600) * 100

    A 1-hour ride at FTP = 100 TSS.
    """
    if ftp <= 0 or duration_seconds <= 0:
        return 0.0
    return (duration_seconds * np * if_) / (ftp * 3600) * 100


def ctl_update(
    previous_ctl: float, today_tss: float, time_constant: int = CTL_TIME_CONSTANT
) -> float:
    """
    Exponentially weighted moving average for Chronic Training Load (fitness).
    CTL_today = CTL_yesterday + (TSS_today - CTL_yesterday) * (1 - e^(-1/tc))
    """
    decay = 1 - math.exp(-1 / time_constant)
    return previous_ctl + (today_tss - previous_ctl) * decay


def atl_update(
    previous_atl: float, today_tss: float, time_constant: int = ATL_TIME_CONSTANT
) -> float:
    """
    Exponentially weighted moving average for Acute Training Load (fatigue).
    ATL_today = ATL_yesterday + (TSS_today - ATL_yesterday) * (1 - e^(-1/tc))
    """
    decay = 1 - math.exp(-1 / time_constant)
    return previous_atl + (today_tss - previous_atl) * decay


def tsb(ctl: float, atl: float) -> float:
    """Training Stress Balance (form) = CTL - ATL."""
    return ctl - atl


def ftp_from_20min_test(twenty_min_avg_power: float) -> int:
    """Estimate FTP from a 20-minute all-out test. FTP = 20min_avg * 0.95."""
    return round(twenty_min_avg_power * FTP_FROM_20MIN_MULTIPLIER)


def ftp_from_best_efforts(efforts: dict[int, float]) -> int:
    """
    Estimate FTP from a collection of best efforts at various durations.

    Args:
        efforts: dict mapping duration_seconds -> best_avg_power
                 e.g. {300: 320, 1200: 280, 3600: 250}

    Returns estimated FTP as integer watts.
    Uses the most reliable estimate available.
    """
    estimates = []

    # 60-minute effort is direct FTP
    if 3600 in efforts and efforts[3600] > 0:
        estimates.append(efforts[3600])

    # 20-minute test
    if 1200 in efforts and efforts[1200] > 0:
        estimates.append(efforts[1200] * FTP_FROM_20MIN_MULTIPLIER)

    # 8-minute test
    if 480 in efforts and efforts[480] > 0:
        estimates.append(efforts[480] * 0.90)

    # 5-minute test
    if 300 in efforts and efforts[300] > 0:
        estimates.append(efforts[300] * 0.75)

    if not estimates:
        return 0

    # Use the highest reliable estimate (longer durations are more reliable)
    return round(max(estimates))


def power_zones(ftp: int) -> dict[str, dict[str, int | str]]:
    """
    Calculate Coggan 7-zone power boundaries from FTP.

    Returns dict like:
    {"Z1": {"name": "Active Recovery", "low": 0, "high": 145}, ...}
    """
    zones = {}
    for zone_id, zone_def in POWER_ZONES.items():
        zones[zone_id] = {
            "name": zone_def["name"],
            "low": round(ftp * zone_def["low"]),
            "high": round(ftp * zone_def["high"]),
        }
    return zones


def hr_zones(
    max_hr: int, resting_hr: int | None = None
) -> dict[str, dict[str, int | str]]:
    """
    Calculate heart rate zones.

    Uses Karvonen formula if resting HR is available:
        target_hr = resting_hr + (max_hr - resting_hr) * intensity

    Otherwise uses simple percentage of max HR.
    """
    zones = {}
    for zone_id, zone_def in HR_ZONES.items():
        if resting_hr is not None:
            hrr = max_hr - resting_hr
            low = round(resting_hr + hrr * zone_def["low"])
            high = round(resting_hr + hrr * zone_def["high"])
        else:
            low = round(max_hr * zone_def["low"])
            high = round(max_hr * zone_def["high"])

        zones[zone_id] = {
            "name": zone_def["name"],
            "low": low,
            "high": high,
        }
    return zones


def w_per_kg(power_watts: int | float, weight_kg: float) -> float:
    """Watts per kilogram. Returns 0.0 if weight is 0."""
    if weight_kg <= 0:
        return 0.0
    return round(power_watts / weight_kg, 2)


def rider_type_profile(
    best_efforts: dict[int, float], ftp: int, weight_kg: float
) -> dict:
    """
    Classify rider type based on power-to-weight at different durations.

    Returns:
        {
            "type": "climber",
            "strengths": ["sustained efforts 10-60min", "climbing"],
            "weaknesses": ["sprint power <15s"]
        }
    """
    if weight_kg <= 0 or ftp <= 0:
        return {"type": "all_rounder", "strengths": [], "weaknesses": []}

    # Calculate W/kg at various durations
    wpkg_at_duration = {}
    for duration, power in best_efforts.items():
        if power > 0:
            wpkg_at_duration[duration] = power / weight_kg

    strengths = []
    weaknesses = []

    # Sprint (5s)
    sprint_wpkg = wpkg_at_duration.get(5, 0)
    if sprint_wpkg >= 18.0:
        strengths.append("explosive sprint power")
    elif sprint_wpkg < 12.0 and sprint_wpkg > 0:
        weaknesses.append("sprint power <15s")

    # Short efforts (1min)
    one_min_wpkg = wpkg_at_duration.get(60, 0)
    if one_min_wpkg >= 7.5:
        strengths.append("anaerobic capacity")
    elif one_min_wpkg < 5.5 and one_min_wpkg > 0:
        weaknesses.append("anaerobic capacity")

    # VO2max (5min)
    five_min_wpkg = wpkg_at_duration.get(300, 0)
    if five_min_wpkg >= 5.5:
        strengths.append("VO2max power")
    elif five_min_wpkg < 4.0 and five_min_wpkg > 0:
        weaknesses.append("VO2max capacity")

    # Threshold (20min)
    twenty_min_wpkg = wpkg_at_duration.get(1200, 0)
    if twenty_min_wpkg >= 4.5:
        strengths.append("sustained threshold efforts")
    elif twenty_min_wpkg < 3.5 and twenty_min_wpkg > 0:
        weaknesses.append("threshold endurance")

    # Endurance (60min)
    sixty_min_wpkg = wpkg_at_duration.get(3600, 0)
    if sixty_min_wpkg >= 4.0:
        strengths.append("long endurance and climbing")
    elif sixty_min_wpkg < 3.0 and sixty_min_wpkg > 0:
        weaknesses.append("sustained endurance")

    # Determine rider type
    ftp_wpkg = ftp / weight_kg

    if sprint_wpkg >= 18.0 and (twenty_min_wpkg < 4.0 or twenty_min_wpkg == 0):
        rider_type = "sprinter"
    elif five_min_wpkg >= 5.5 and sprint_wpkg < 16.0:
        rider_type = "pursuiter"
    elif ftp_wpkg >= 4.0 and sixty_min_wpkg >= 3.8:
        rider_type = "climber"
    elif twenty_min_wpkg >= 4.5 and sprint_wpkg < 16.0:
        rider_type = "time_trialist"
    else:
        rider_type = "all_rounder"

    return {
        "type": rider_type,
        "strengths": strengths,
        "weaknesses": weaknesses,
    }


def rider_profile_scores(
    best_efforts_data: dict[int, float], weight_kg: float
) -> dict[str, float]:
    """
    Compute 0-100 scores for each rider profile category by interpolating
    the rider's W/kg against known benchmarks (Coggan power profile chart).

    Used for the radar chart visualization.

    Returns: {"sprint": 72.5, "anaerobic": 55.0, "vo2max": 60.0, ...}
    """
    from app.core.constants import POWER_BENCHMARKS_WPKG, RIDER_PROFILE_CATEGORIES

    if weight_kg <= 0:
        return {cat: 0.0 for cat in RIDER_PROFILE_CATEGORIES}

    scores: dict[str, float] = {}
    for category, info in RIDER_PROFILE_CATEGORIES.items():
        duration = info["duration"]
        power = best_efforts_data.get(duration, 0)
        if power <= 0:
            scores[category] = 0.0
            continue

        wpkg = power / weight_kg
        benchmarks = POWER_BENCHMARKS_WPKG.get(duration, [])
        if not benchmarks:
            scores[category] = 0.0
            continue

        # Linear interpolation between benchmark levels
        n = len(benchmarks)
        if wpkg <= benchmarks[0]:
            # Below untrained — proportional score in first bucket
            score = (wpkg / benchmarks[0]) * (100.0 / n)
        elif wpkg >= benchmarks[-1]:
            score = 100.0
        else:
            score = 50.0  # fallback
            for i in range(n - 1):
                if benchmarks[i] <= wpkg <= benchmarks[i + 1]:
                    frac = (wpkg - benchmarks[i]) / (benchmarks[i + 1] - benchmarks[i])
                    score = ((i + frac) / (n - 1)) * 100.0
                    break

        scores[category] = round(score, 1)

    return scores


def time_in_zones(
    power_samples: list[int | float], ftp: int
) -> dict[str, int]:
    """
    Calculate seconds spent in each power zone.

    Returns dict like: {"Z1": 1200, "Z2": 1800, ...}
    Assumes 1Hz sample rate (1 sample = 1 second).
    """
    zones = power_zones(ftp)
    time_in = {z: 0 for z in zones}

    for power in power_samples:
        if power is None or power < 0:
            continue
        for zone_id, zone_bounds in zones.items():
            if zone_bounds["low"] <= power <= zone_bounds["high"]:
                time_in[zone_id] += 1
                break
        else:
            # Power above Z7 high still counts as Z7
            if power > zones["Z7"]["high"]:
                time_in["Z7"] += 1

    return time_in


def best_efforts(
    power_samples: list[int | float], durations: list[int]
) -> dict[int, float]:
    """
    Find best average power for each duration from power data.

    Args:
        power_samples: list of power readings at 1Hz
        durations: list of durations in seconds to find best effort for

    Returns dict mapping duration -> best average power
    """
    results = {}
    samples = [max(0, p) if p is not None else 0 for p in power_samples]

    for duration in durations:
        if len(samples) < duration:
            results[duration] = 0.0
            continue

        best = 0.0
        # Sliding window
        window_sum = sum(samples[:duration])
        best = window_sum / duration

        for i in range(1, len(samples) - duration + 1):
            window_sum = window_sum - samples[i - 1] + samples[i + duration - 1]
            avg = window_sum / duration
            if avg > best:
                best = avg

        results[duration] = round(best, 1)

    return results
