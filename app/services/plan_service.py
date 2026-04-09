"""
Training plan generation service.

Generates truly personalised training plans based on:
- Goal event (date, type, priority, terrain)
- Current fitness (CTL, ATL, TSB)
- Rider profile (strengths, weaknesses)
- Experience level and available hours
- Progressive overload with recovery weeks
"""

from datetime import date, timedelta
from math import ceil

from sqlalchemy.orm import Session

from app.core.workout_templates import (
    PHASE_WORKOUT_MIX,
    WORKOUT_TEMPLATES,
    estimate_tss,
    get_template,
)
from app.models.onboarding import GoalEvent, GoalStatus
from app.models.training import (
    PeriodizationModel,
    PhaseType,
    PlanStatus,
    TrainingPhase,
    TrainingPlan,
    Workout,
    WorkoutStatus,
    WorkoutStep,
    WorkoutType,
)
from app.models.user import User
from app.services.metrics_service import get_current_fitness


# --- Goal-specific workout emphasis ---
# Maps event type to workout type weights for build/peak phases.
# Higher weight = more sessions of that type scheduled.
GOAL_WORKOUT_EMPHASIS = {
    "time_trial": {
        "threshold": 3, "sweet_spot": 2, "endurance": 2, "vo2max": 1, "tempo": 1, "recovery": 1,
    },
    "hill_climb": {
        "vo2max": 2, "threshold": 3, "sweet_spot": 2, "endurance": 2, "recovery": 1,
    },
    "road_race": {
        "vo2max": 2, "threshold": 2, "sweet_spot": 1, "endurance": 2, "sprint": 1, "recovery": 1,
    },
    "crit": {
        "vo2max": 2, "sprint": 2, "threshold": 2, "endurance": 1, "recovery": 1,
    },
    "sportive": {
        "endurance": 3, "sweet_spot": 2, "tempo": 2, "threshold": 1, "recovery": 1,
    },
    "gran_fondo": {
        "endurance": 3, "sweet_spot": 2, "tempo": 2, "threshold": 1, "recovery": 1,
    },
    "gravel": {
        "endurance": 3, "sweet_spot": 2, "tempo": 1, "threshold": 1, "recovery": 1,
    },
    "mtb": {
        "vo2max": 2, "endurance": 2, "sweet_spot": 1, "threshold": 1, "sprint": 1, "recovery": 1,
    },
    "stage_race": {
        "endurance": 2, "threshold": 2, "sweet_spot": 2, "vo2max": 1, "recovery": 1,
    },
    "century": {
        "endurance": 4, "sweet_spot": 2, "tempo": 2, "recovery": 1,
    },
    "charity_ride": {
        "endurance": 3, "sweet_spot": 1, "tempo": 1, "recovery": 1,
    },
}

# Default emphasis when no goal or unknown type
DEFAULT_EMPHASIS = {
    "endurance": 2, "sweet_spot": 2, "threshold": 1, "tempo": 1, "recovery": 1,
}


def _get_recovery_cycle(experience: str | None) -> int:
    """How many hard weeks before a recovery week."""
    if experience in ("beginner", None):
        return 2  # 2 hard + 1 easy
    if experience == "intermediate":
        return 3  # 3 hard + 1 easy
    return 3  # advanced/elite: 3 hard + 1 easy (but higher load)


def _ramp_rate_tss_per_week(experience: str | None) -> float:
    """Weekly TSS increase during hard weeks."""
    if experience in ("beginner", None):
        return 15
    if experience == "intermediate":
        return 25
    return 35  # advanced/elite


def _starting_weekly_tss(current_ctl: float, current_tsb: float) -> float:
    """
    Determine starting weekly TSS based on current fitness.
    Weekly TSS ≈ CTL × 7 (CTL is daily average stress).
    If very fatigued (TSB < -20), start lower.
    """
    base_tss = max(100, current_ctl * 7)

    if current_tsb < -30:
        # Very fatigued — start with a recovery-level week
        return base_tss * 0.6
    if current_tsb < -15:
        # Moderately fatigued — ease in
        return base_tss * 0.8

    return base_tss


def _days_per_week(weekly_hours: float, experience: str | None) -> int:
    """Determine training days per week based on available hours."""
    if weekly_hours <= 4:
        return 3
    if weekly_hours <= 6:
        return 4
    if weekly_hours <= 10:
        return 5
    return 6


def _build_weekly_workout_types(
    phase_type: str,
    days: int,
    goal_emphasis: dict[str, int],
    is_recovery_week: bool = False,
) -> list[str]:
    """
    Build a workout type list for a week, tailored to phase and goal.
    Recovery weeks shift to more endurance/recovery.
    """
    if is_recovery_week:
        # Recovery week: easy volume, no intensity
        types = ["recovery", "endurance"]
        while len(types) < days:
            types.append("endurance" if len(types) % 2 == 0 else "recovery")
        return types[:days]

    # Phase-specific base distribution
    if phase_type == "base":
        # Base: mostly endurance with some tempo/sweet spot sneaking in
        pool = {"endurance": 3, "tempo": 1, "recovery": 1}
        # Slightly influenced by goal even in base
        for wtype in ("sweet_spot", "tempo"):
            if wtype in goal_emphasis and goal_emphasis[wtype] >= 2:
                pool[wtype] = pool.get(wtype, 0) + 1
    elif phase_type == "build":
        # Build: goal-specific intensity ramps up
        pool = dict(goal_emphasis)
    elif phase_type == "peak":
        # Peak: high intensity, lower volume — sharpen
        pool = {}
        for wtype, weight in goal_emphasis.items():
            if wtype in ("vo2max", "threshold", "sprint"):
                pool[wtype] = weight + 1  # boost intensity types
            elif wtype == "recovery":
                pool[wtype] = weight + 1  # more recovery in peak
            else:
                pool[wtype] = max(1, weight - 1)  # reduce volume types
    elif phase_type == "race":
        # Race week: taper — openers + recovery
        pool = {"recovery": 3, "vo2max": 1, "endurance": 1}
    else:
        pool = {"endurance": 2, "recovery": 1}

    # Expand pool into ordered list (weighted)
    expanded = []
    for wtype, weight in pool.items():
        expanded.extend([wtype] * weight)

    # Select days worth of types, prioritising variety
    selected = []
    # Always start week with endurance if available
    if "endurance" in expanded and phase_type != "race":
        selected.append("endurance")
        expanded.remove("endurance")

    # Fill remaining days, avoiding consecutive same types
    while len(selected) < days and expanded:
        # Prefer types not recently added
        last = selected[-1] if selected else None
        candidates = [t for t in expanded if t != last]
        if not candidates:
            candidates = expanded
        pick = candidates[0]
        selected.append(pick)
        expanded.remove(pick)

    # If still short, pad with endurance/recovery
    while len(selected) < days:
        selected.append("endurance" if len(selected) % 3 != 0 else "recovery")

    # Always end week with recovery if we have 4+ days
    if days >= 4 and selected[-1] != "recovery":
        # Swap last non-recovery with recovery at end
        if "recovery" in selected:
            selected.remove("recovery")
            selected.append("recovery")
        else:
            selected[-1] = "recovery"

    return selected[:days]


def generate_plan(
    db: Session,
    user: User,
    goal_event_id: str | None = None,
    periodization_model: str = "traditional",
    name: str | None = None,
) -> TrainingPlan:
    """
    Generate a personalised periodized training plan.

    Adapts to:
    - Current fitness (CTL/ATL/TSB) for appropriate starting load
    - Goal event type for workout selection emphasis
    - Experience level for ramp rate and recovery frequency
    - Available hours for volume scaling
    - Progressive overload with scheduled recovery weeks
    """
    today = date.today()

    # ── 1. Cancel any existing active plans ──
    existing_active = (
        db.query(TrainingPlan)
        .filter(
            TrainingPlan.user_id == user.id,
            TrainingPlan.status == PlanStatus.active,
        )
        .all()
    )
    for old_plan in existing_active:
        old_plan.status = PlanStatus.cancelled
    if existing_active:
        db.flush()

    # ── 2. Gather context ──
    goal_event = None
    end_date = today + timedelta(weeks=12)

    if goal_event_id:
        goal_event = db.query(GoalEvent).filter(
            GoalEvent.id == goal_event_id,
            GoalEvent.user_id == user.id,
        ).first()
        if goal_event:
            end_date = goal_event.event_date

    weeks_available = max(4, (end_date - today).days // 7)

    # Current fitness
    fitness = get_current_fitness(db, user.id)
    current_ctl = fitness["ctl"]
    current_atl = fitness["atl"]
    current_tsb = fitness["tsb"]

    # User context
    ftp = user.ftp or 200
    weekly_hours = user.weekly_hours_available or 6
    experience = user.experience_level or "intermediate"

    # Goal emphasis
    goal_type = goal_event.event_type if goal_event else None
    goal_emphasis = GOAL_WORKOUT_EMPHASIS.get(goal_type, DEFAULT_EMPHASIS)
    goal_priority = goal_event.priority if goal_event else None

    # ── 3. Plan naming ──
    if name is None:
        if goal_event:
            name = f"Plan for {goal_event.event_name}"
        else:
            name = f"Training Plan - {today.strftime('%b %Y')}"

    # ── 4. Create plan ──
    plan = TrainingPlan(
        user_id=user.id,
        name=name,
        goal_event_id=goal_event_id,
        start_date=today,
        end_date=end_date,
        status=PlanStatus.active,
        periodization_model=periodization_model,
    )
    db.add(plan)
    db.flush()

    # ── 5. Collect race dates to avoid ──
    all_goals = db.query(GoalEvent).filter(
        GoalEvent.user_id == user.id,
        GoalEvent.event_date >= today,
        GoalEvent.status == GoalStatus.upcoming,
    ).all()
    goal_event_dates = {g.event_date for g in all_goals}

    # ── 6. Build phases ──
    phases = _build_phases(weeks_available, today, end_date, periodization_model)

    # ── 7. Calculate progressive TSS targets ──
    starting_tss = _starting_weekly_tss(current_ctl, current_tsb)
    ramp_per_week = _ramp_rate_tss_per_week(experience)
    recovery_cycle = _get_recovery_cycle(experience)
    training_days = _days_per_week(weekly_hours, experience)

    # ── 8. Generate workouts per phase ──
    sort_order = 0
    cumulative_week = 0

    for phase_def in phases:
        phase = TrainingPhase(
            plan_id=plan.id,
            phase_type=phase_def["type"],
            start_date=phase_def["start_date"],
            end_date=phase_def["end_date"],
            target_weekly_hours=weekly_hours,
            focus=phase_def.get("focus"),
            sort_order=sort_order,
        )
        db.add(phase)
        db.flush()
        sort_order += 1

        # Generate fitness-aware workouts
        cumulative_week = _generate_adaptive_workouts(
            db=db,
            phase=phase,
            user=user,
            ftp=ftp,
            weekly_hours=weekly_hours,
            training_days=training_days,
            starting_tss=starting_tss,
            ramp_per_week=ramp_per_week,
            recovery_cycle=recovery_cycle,
            goal_emphasis=goal_emphasis,
            goal_event_dates=goal_event_dates,
            cumulative_week=cumulative_week,
        )

    db.commit()
    db.refresh(plan)
    return plan


def _generate_adaptive_workouts(
    db: Session,
    phase: TrainingPhase,
    user: User,
    ftp: int,
    weekly_hours: float,
    training_days: int,
    starting_tss: float,
    ramp_per_week: float,
    recovery_cycle: int,
    goal_emphasis: dict[str, int],
    goal_event_dates: set,
    cumulative_week: int,
) -> int:
    """
    Generate workouts for a phase with progressive overload and recovery weeks.
    Returns the updated cumulative_week count.
    """
    start = phase.start_date
    end = phase.end_date
    if isinstance(start, str):
        start = date.fromisoformat(start)
    if isinstance(end, str):
        end = date.fromisoformat(end)

    phase_type = phase.phase_type
    current_week_start = start
    workout_sort_order = 0

    # Phase-specific TSS multipliers
    phase_tss_mult = {
        "base": 0.85,       # lower intensity
        "build": 1.0,       # full progression
        "peak": 0.9,        # slightly reduced volume, higher intensity
        "race": 0.5,        # taper
        "recovery": 0.5,
        "off_season": 0.6,
    }
    mult = phase_tss_mult.get(phase_type, 1.0)

    while current_week_start <= end:
        week_end = min(current_week_start + timedelta(days=6), end)
        days_in_week = (week_end - current_week_start).days + 1

        # Is this a recovery week?
        is_recovery = (
            cumulative_week > 0
            and cumulative_week % (recovery_cycle + 1) == recovery_cycle
            and phase_type not in ("race", "recovery")
        )

        # Calculate target weekly TSS with progression
        if is_recovery:
            target_weekly_tss = starting_tss * 0.6  # 60% of base for recovery
        else:
            target_weekly_tss = (starting_tss + ramp_per_week * cumulative_week) * mult

        # Update phase target
        phase.target_weekly_tss = round(target_weekly_tss, 1)

        # Determine workout types for this week
        actual_days = min(training_days, days_in_week)
        workout_types = _build_weekly_workout_types(
            phase_type, actual_days, goal_emphasis, is_recovery,
        )

        # Distribute TSS across workouts (intensity sessions get more TSS)
        intensity_types = {"threshold", "vo2max", "sweet_spot", "sprint"}
        tss_weights = []
        for wtype in workout_types:
            if wtype in intensity_types:
                tss_weights.append(1.3)
            elif wtype == "recovery":
                tss_weights.append(0.5)
            else:
                tss_weights.append(1.0)
        total_weight = sum(tss_weights)

        # ── Schedule workouts respecting user day preferences ──
        hard_days = set(user.preferred_hard_days or [])
        user_rest_days = set(user.rest_days or [])
        intensity_types = {"threshold", "vo2max", "sweet_spot", "sprint"}

        # 1. Build available days (exclude rest days and race days)
        available = []
        for d in range(days_in_week):
            day_date = current_week_start + timedelta(days=d)
            dow = day_date.weekday()
            if dow in user_rest_days:
                continue
            if goal_event_dates and day_date in goal_event_dates:
                continue
            if day_date > end:
                continue
            available.append((dow, day_date))

        if not available:
            cumulative_week += 1
            current_week_start += timedelta(weeks=1)
            continue

        # 2. Pick which days to train (up to actual_days)
        #    Prioritise hard days (always include them), fill rest with easy days
        hard_slots = [a for a in available if a[0] in hard_days]
        easy_slots = [a for a in available if a[0] not in hard_days]
        selected_days = hard_slots[:]  # always include all hard days
        remaining_needed = actual_days - len(selected_days)
        if remaining_needed > 0:
            # Spread easy days evenly
            step_sz = max(1, len(easy_slots) // remaining_needed) if remaining_needed else 1
            selected_days += easy_slots[::step_sz][:remaining_needed]
        selected_days.sort(key=lambda x: x[0])  # sort by day of week
        selected_days = selected_days[:actual_days]

        # 3. Split workout types into hard and easy
        hard_types = [wt for wt in workout_types if wt in intensity_types]
        easy_types = [wt for wt in workout_types if wt not in intensity_types]

        # 4. Assign: hard types to hard days, easy types to easy days
        ordered = []
        for dow, _ in selected_days:
            if dow in hard_days and hard_types:
                ordered.append(hard_types.pop(0))
            elif easy_types:
                ordered.append(easy_types.pop(0))
            elif hard_types:
                ordered.append(hard_types.pop(0))
            else:
                ordered.append("endurance")

        # 5. Calculate TSS weights
        tss_weights = []
        for wt in ordered:
            if wt in intensity_types:
                tss_weights.append(1.3)
            elif wt == "recovery":
                tss_weights.append(0.5)
            else:
                tss_weights.append(1.0)
        total_weight = sum(tss_weights) or 1

        for slot_idx, (dow, workout_day) in enumerate(selected_days):
            if slot_idx >= len(ordered):
                break
            wtype = ordered[slot_idx]

            # Calculate per-workout TSS target
            workout_tss_target = target_weekly_tss * (tss_weights[slot_idx] / total_weight)

            # Pick template closest to TSS target (via duration hint)
            # TSS ≈ (hours) × IF² × 100, so target_hours ≈ TSS / (IF² × 100)
            template = get_template(wtype)
            planned_if = template.get("planned_if", 0.65)
            target_duration_s = int(workout_tss_target / (planned_if ** 2 * 100) * 3600)
            # Clamp to reasonable bounds
            target_duration_s = max(1800, min(target_duration_s, int(weekly_hours * 3600 * 0.4)))

            template = get_template(wtype, duration_hint=target_duration_s)
            planned_tss = estimate_tss(template, ftp)

            workout = Workout(
                phase_id=phase.id,
                user_id=user.id,
                scheduled_date=workout_day,
                title=template["name"],
                description=template.get("description", ""),
                workout_type=wtype,
                planned_duration_seconds=template["duration_seconds"],
                planned_tss=round(planned_tss, 1),
                planned_if=template.get("planned_if"),
                status=WorkoutStatus.planned,
                sort_order=workout_sort_order,
            )
            db.add(workout)
            db.flush()
            workout_sort_order += 1

            _create_workout_steps(db, workout, template)

        cumulative_week += 1
        current_week_start += timedelta(weeks=1)

    return cumulative_week


def _build_phases(
    weeks_available: int,
    start_date: date,
    end_date: date,
    model: str,
) -> list[dict]:
    """
    Determine training phases based on weeks available and periodization model.

    Traditional: base -> build -> peak -> race -> recovery
    Polarized: base(long) -> build(short) -> peak -> race
    Sweet Spot: base(sweet spot focus) -> build -> peak -> race
    """
    phases = []
    current_date = start_date

    if weeks_available <= 4:
        mid = current_date + timedelta(weeks=weeks_available // 2)
        phases.append({
            "type": PhaseType.build,
            "start_date": current_date,
            "end_date": mid - timedelta(days=1),
            "focus": "Build fitness quickly with goal-specific intensity",
        })
        phases.append({
            "type": PhaseType.peak,
            "start_date": mid,
            "end_date": end_date,
            "focus": "Sharpen form — maintain intensity, reduce volume",
        })
        return phases

    if weeks_available <= 8:
        base_weeks = max(2, weeks_available // 3)
        build_weeks = max(2, (weeks_available - base_weeks) // 2)
        peak_weeks = weeks_available - base_weeks - build_weeks

        d1 = current_date + timedelta(weeks=base_weeks)
        d2 = d1 + timedelta(weeks=build_weeks)

        phases.append({
            "type": PhaseType.base,
            "start_date": current_date,
            "end_date": d1 - timedelta(days=1),
            "focus": "Build aerobic foundation and establish training consistency",
        })
        phases.append({
            "type": PhaseType.build,
            "start_date": d1,
            "end_date": d2 - timedelta(days=1),
            "focus": "Increase intensity with goal-specific workouts",
        })
        phases.append({
            "type": PhaseType.peak,
            "start_date": d2,
            "end_date": end_date,
            "focus": "Sharpen and taper — key sessions only",
        })
        return phases

    # Full plan (8+ weeks)
    if model == PeriodizationModel.polarized:
        base_weeks = max(4, int(weeks_available * 0.50))
        build_weeks = max(2, int(weeks_available * 0.25))
        peak_weeks = max(1, int(weeks_available * 0.15))
        race_weeks = weeks_available - base_weeks - build_weeks - peak_weeks
    elif model == PeriodizationModel.sweet_spot:
        base_weeks = max(3, int(weeks_available * 0.35))
        build_weeks = max(3, int(weeks_available * 0.35))
        peak_weeks = max(1, int(weeks_available * 0.15))
        race_weeks = weeks_available - base_weeks - build_weeks - peak_weeks
    else:
        # Traditional
        base_weeks = max(3, int(weeks_available * 0.40))
        build_weeks = max(2, int(weeks_available * 0.30))
        peak_weeks = max(1, int(weeks_available * 0.15))
        race_weeks = weeks_available - base_weeks - build_weeks - peak_weeks

    d1 = current_date + timedelta(weeks=base_weeks)
    d2 = d1 + timedelta(weeks=build_weeks)
    d3 = d2 + timedelta(weeks=peak_weeks)

    phases.append({
        "type": PhaseType.base,
        "start_date": current_date,
        "end_date": d1 - timedelta(days=1),
        "focus": "Aerobic base — endurance foundation and movement efficiency",
    })
    phases.append({
        "type": PhaseType.build,
        "start_date": d1,
        "end_date": d2 - timedelta(days=1),
        "focus": "Build race-specific fitness — progressive intensity",
    })
    phases.append({
        "type": PhaseType.peak,
        "start_date": d2,
        "end_date": d3 - timedelta(days=1),
        "focus": "Peak — reduce volume, maintain sharpness",
    })
    if race_weeks > 0:
        phases.append({
            "type": PhaseType.race,
            "start_date": d3,
            "end_date": end_date,
            "focus": "Race week — taper, activate, perform",
        })

    return phases


def _create_workout_steps(
    db: Session, workout: Workout, template: dict
) -> None:
    """Create WorkoutStep rows from template steps."""
    steps = template.get("steps", [])
    step_order = 0

    for step_def in steps:
        repeat = step_def.get("repeat_count")
        actual_repeats = repeat if repeat and repeat > 1 else 1

        if step_def["step_type"] in ("interval_on", "interval_off") and actual_repeats > 1:
            step = WorkoutStep(
                workout_id=workout.id,
                step_order=step_order,
                step_type=step_def["step_type"],
                duration_seconds=step_def["duration_seconds"],
                power_target_pct=step_def.get("power_target_pct"),
                power_low_pct=step_def.get("power_low_pct"),
                power_high_pct=step_def.get("power_high_pct"),
                cadence_target=step_def.get("cadence_target"),
                repeat_count=actual_repeats,
                notes=step_def.get("notes"),
            )
            db.add(step)
            step_order += 1
        else:
            step = WorkoutStep(
                workout_id=workout.id,
                step_order=step_order,
                step_type=step_def["step_type"],
                duration_seconds=step_def["duration_seconds"],
                power_target_pct=step_def.get("power_target_pct"),
                power_low_pct=step_def.get("power_low_pct"),
                power_high_pct=step_def.get("power_high_pct"),
                cadence_target=step_def.get("cadence_target"),
                repeat_count=step_def.get("repeat_count"),
                notes=step_def.get("notes"),
            )
            db.add(step)
            step_order += 1


# --- Query functions ---

def get_plans(db: Session, user_id: str) -> list[TrainingPlan]:
    """Get all training plans for a user."""
    return (
        db.query(TrainingPlan)
        .filter(TrainingPlan.user_id == user_id)
        .order_by(TrainingPlan.created_at.desc())
        .all()
    )


def get_plan(db: Session, plan_id: str, user_id: str) -> TrainingPlan | None:
    """Get a single plan with phases loaded."""
    return (
        db.query(TrainingPlan)
        .filter(TrainingPlan.id == plan_id, TrainingPlan.user_id == user_id)
        .first()
    )


def get_plan_workouts(
    db: Session, plan_id: str, user_id: str,
    start_date: date | None = None, end_date: date | None = None,
) -> list[Workout]:
    """Get all workouts for a plan, optionally filtered by date."""
    plan = get_plan(db, plan_id, user_id)
    if not plan:
        return []

    phase_ids = [p.id for p in plan.phases]
    if not phase_ids:
        return []

    query = (
        db.query(Workout)
        .filter(Workout.phase_id.in_(phase_ids))
    )

    if start_date:
        query = query.filter(Workout.scheduled_date >= start_date)
    if end_date:
        query = query.filter(Workout.scheduled_date <= end_date)

    return query.order_by(Workout.scheduled_date, Workout.sort_order).all()


def get_workouts_by_date(
    db: Session, user_id: str,
    target_date: date | None = None,
    week_start: date | None = None,
) -> list[Workout]:
    """Get workouts for a specific date or week — only from active plans."""
    # Join through phase → plan to filter by active status
    query = (
        db.query(Workout)
        .join(TrainingPhase, Workout.phase_id == TrainingPhase.id)
        .join(TrainingPlan, TrainingPhase.plan_id == TrainingPlan.id)
        .filter(
            Workout.user_id == user_id,
            TrainingPlan.status == PlanStatus.active,
        )
    )

    if target_date:
        query = query.filter(Workout.scheduled_date == target_date)
    elif week_start:
        week_end = week_start + timedelta(days=6)
        query = query.filter(
            Workout.scheduled_date >= week_start,
            Workout.scheduled_date <= week_end,
        )

    return query.order_by(Workout.scheduled_date, Workout.sort_order).all()


def get_workout(db: Session, workout_id: str, user_id: str) -> Workout | None:
    """Get a single workout with steps loaded."""
    return (
        db.query(Workout)
        .filter(Workout.id == workout_id, Workout.user_id == user_id)
        .first()
    )


def update_workout_status(
    db: Session, workout: Workout, status: str, ride_id: str | None = None
) -> Workout:
    """Update workout status and optionally link a ride."""
    WorkoutStatus(status)  # validate
    workout.status = status
    if ride_id:
        workout.actual_ride_id = ride_id
    db.commit()
    db.refresh(workout)
    return workout


def link_ride_to_workout(
    db: Session, workout: Workout, ride_id: str
) -> Workout:
    """Link an actual ride to a planned workout."""
    workout.actual_ride_id = ride_id
    workout.status = WorkoutStatus.completed
    db.commit()
    db.refresh(workout)
    return workout
