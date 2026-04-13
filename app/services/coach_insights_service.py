"""
Coach Insights Service — Marco's proactive presence across the app.

Three types of insight:
1. Daily nudge — contextual coaching card on the dashboard
2. Ride debrief — auto-generated post-ride feedback (standalone, not tied to a workout)
3. Metric explanation — tap-to-explain any metric in YOUR context

Uses Claude Haiku for nudges and explanations (fast, cheap),
Claude Sonnet for debriefs (deeper analysis).
"""

import json
import logging
from datetime import date, datetime, timedelta

import anthropic
from sqlalchemy.orm import Session

from app.config import settings
from app.models.ride import Ride
from app.models.training import TrainingPlan, TrainingPhase, Workout, PlanStatus, WorkoutStatus
from app.models.user import User
from app.services.metrics_service import get_current_fitness, get_weekly_training_load

logger = logging.getLogger(__name__)

# Cost-aware model selection
HAIKU_MODEL = "claude-haiku-4-5-20251001"
SONNET_MODEL = "claude-sonnet-4-20250514"


# ── Daily Nudge ──────────────────────────────────────────────────────────────

NUDGE_SYSTEM_PROMPT = """\
You are Coach Marco, a warm and knowledgeable cycling coach. Generate a SHORT \
coaching nudge (2-3 sentences max) based on the rider's current state.

Rules:
1. Address the rider by first name.
2. Be supportive, specific, and actionable. Never generic.
3. Reference actual numbers from the data (CTL, TSB, recent rides, today's workout).
4. Match your tone to the situation: encouraging on rest days, motivating before hard sessions, \
   celebrating consistency, cautioning when fatigued.
5. Return ONLY the nudge text — no JSON, no markdown headings, just the message.
6. Keep it conversational, like a text from a coach you trust."""


def _build_nudge_context(
    db: Session, user: User
) -> dict:
    """Build lightweight context for nudge generation."""
    today = date.today()
    rider_name = (user.full_name or user.email.split("@")[0]).split()[0]

    # Current fitness
    fitness = get_current_fitness(db, user.id)

    # Today's planned workout (if any)
    today_workout = (
        db.query(Workout)
        .join(TrainingPhase)
        .join(TrainingPlan)
        .filter(
            Workout.user_id == user.id,
            Workout.scheduled_date == today,
            TrainingPlan.status == PlanStatus.active,
        )
        .first()
    )

    # Yesterday's ride (most recent)
    yesterday = today - timedelta(days=1)
    recent_ride = (
        db.query(Ride)
        .filter(
            Ride.user_id == user.id,
            Ride.ride_date >= datetime.combine(yesterday, datetime.min.time()),
        )
        .order_by(Ride.ride_date.desc())
        .first()
    )

    # Weekly load trend (last 4 weeks)
    weekly_load = get_weekly_training_load(db, user.id, weeks=4)

    # Compliance: completed vs total workouts this week
    week_start = today - timedelta(days=today.weekday())
    week_workouts = (
        db.query(Workout)
        .join(TrainingPhase)
        .join(TrainingPlan)
        .filter(
            Workout.user_id == user.id,
            Workout.scheduled_date >= week_start,
            Workout.scheduled_date <= today,
            TrainingPlan.status == PlanStatus.active,
        )
        .all()
    )
    completed = sum(1 for w in week_workouts if w.status == WorkoutStatus.completed)
    total = len(week_workouts)

    context = {
        "rider_name": rider_name,
        "today": today.isoformat(),
        "day_of_week": today.strftime("%A"),
        "fitness": {
            "ctl": round(fitness["ctl"], 1),
            "atl": round(fitness["atl"], 1),
            "tsb": round(fitness["tsb"], 1),
            "ramp_rate": fitness.get("ramp_rate"),
        },
        "ftp": user.ftp,
        "this_week_compliance": f"{completed}/{total} sessions completed",
    }

    if today_workout:
        context["todays_workout"] = {
            "title": today_workout.title,
            "type": today_workout.workout_type,
            "planned_duration_minutes": (today_workout.planned_duration_seconds or 0) // 60,
            "planned_tss": today_workout.planned_tss,
            "status": today_workout.status,
        }
    else:
        context["todays_workout"] = None  # Rest day

    if recent_ride:
        context["last_ride"] = {
            "title": recent_ride.title,
            "date": str(recent_ride.ride_date.date() if hasattr(recent_ride.ride_date, 'date') else recent_ride.ride_date),
            "tss": recent_ride.tss,
            "duration_minutes": (recent_ride.moving_time_seconds or recent_ride.duration_seconds or 0) // 60,
            "normalized_power": recent_ride.normalized_power,
            "intensity_factor": recent_ride.intensity_factor,
        }

    if weekly_load:
        context["weekly_tss_trend"] = [
            {"week": w.get("week_start", ""), "tss": w.get("total_tss", 0)}
            for w in weekly_load[:4]
        ]

    return context


def generate_daily_nudge(db: Session, user: User) -> dict:
    """
    Generate today's coaching nudge. Returns {"nudge": str, "generated_at": str}.
    Cached per user per day via coach_nudges table.
    """
    today = date.today()

    # Check cache
    from app.models.coach import CoachNudge
    existing = (
        db.query(CoachNudge)
        .filter(
            CoachNudge.user_id == user.id,
            CoachNudge.nudge_date == today,
        )
        .first()
    )
    if existing:
        return {
            "nudge": existing.content,
            "generated_at": str(existing.created_at),
            "cached": True,
        }

    # Build context and generate
    context = _build_nudge_context(db, user)

    try:
        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        response = client.messages.create(
            model=HAIKU_MODEL,
            max_tokens=200,
            system=NUDGE_SYSTEM_PROMPT,
            messages=[{
                "role": "user",
                "content": f"Generate today's coaching nudge based on this data:\n\n```json\n{json.dumps(context, indent=2, default=str)}\n```",
            }],
        )
        nudge_text = response.content[0].text.strip()
    except Exception as e:
        logger.error(f"Nudge generation failed: {e}")
        # Deterministic fallback
        rider_name = context["rider_name"]
        tsb = context["fitness"]["tsb"]
        workout = context.get("todays_workout")
        if workout:
            nudge_text = f"Hey {rider_name}, you've got a {workout['type']} session on the plan today. Your form is sitting at {tsb:+.0f} — let's make it count."
        else:
            nudge_text = f"Rest day, {rider_name}. Your body builds fitness during recovery, not just during training. Enjoy the day off."

    # Cache
    nudge = CoachNudge(
        user_id=user.id,
        nudge_date=today,
        content=nudge_text,
    )
    db.add(nudge)
    db.commit()

    return {
        "nudge": nudge_text,
        "generated_at": datetime.utcnow().isoformat(),
        "cached": False,
    }


# ── Ride Debrief ─────────────────────────────────────────────────────────────

DEBRIEF_SYSTEM_PROMPT = """\
You are Coach Marco, a supportive cycling coach. The rider just completed a ride \
and you are giving them a brief, encouraging debrief.

Rules:
1. Address the rider by first name.
2. Keep it to 2-3 short paragraphs. Warm, specific, data-informed.
3. Highlight what went well FIRST. Then note anything to watch.
4. Reference specific numbers from the ride (power, duration, TSS, IF).
5. If you can relate this ride to their fitness trend or upcoming goal, do so briefly.
6. End with a forward-looking statement (what's next, how this builds toward their goal).
7. Return ONLY the debrief text as plain paragraphs (markdown OK for bold/italic). No JSON."""


def _build_debrief_context(
    db: Session, user: User, ride: Ride
) -> dict:
    """Build context for ride debrief generation."""
    rider_name = (user.full_name or user.email.split("@")[0]).split()[0]
    fitness = get_current_fitness(db, user.id)

    # Linked workout (if any)
    linked_workout = None
    if ride.workout_id:
        linked_workout = db.query(Workout).filter(Workout.id == ride.workout_id).first()

    # Upcoming goal
    from app.models.onboarding import GoalEvent, GoalStatus
    upcoming_goal = (
        db.query(GoalEvent)
        .filter(
            GoalEvent.user_id == user.id,
            GoalEvent.event_date >= date.today(),
            GoalEvent.status == GoalStatus.upcoming,
        )
        .order_by(GoalEvent.event_date)
        .first()
    )

    context = {
        "rider_name": rider_name,
        "ride": {
            "title": ride.title,
            "date": str(ride.ride_date),
            "duration_minutes": (ride.moving_time_seconds or ride.duration_seconds or 0) // 60,
            "distance_km": round((ride.distance_meters or 0) / 1000, 1),
            "elevation_m": round(ride.elevation_gain_meters or 0),
            "average_power": ride.average_power,
            "normalized_power": ride.normalized_power,
            "intensity_factor": ride.intensity_factor,
            "tss": ride.tss,
            "average_hr": ride.average_hr,
        },
        "fitness_after": {
            "ctl": round(fitness["ctl"], 1),
            "atl": round(fitness["atl"], 1),
            "tsb": round(fitness["tsb"], 1),
        },
        "ftp": user.ftp,
    }

    if linked_workout:
        context["planned_workout"] = {
            "title": linked_workout.title,
            "type": linked_workout.workout_type,
            "planned_duration_minutes": (linked_workout.planned_duration_seconds or 0) // 60,
            "planned_tss": linked_workout.planned_tss,
            "planned_if": linked_workout.planned_if,
        }

    if upcoming_goal:
        days_until = (upcoming_goal.event_date - date.today()).days
        context["upcoming_goal"] = {
            "event_name": upcoming_goal.event_name,
            "event_date": str(upcoming_goal.event_date),
            "days_until": days_until,
            "priority": str(upcoming_goal.priority),
        }

    return context


def generate_ride_debrief(
    db: Session, user: User, ride: Ride, force: bool = False
) -> dict:
    """
    Generate a coaching debrief for a completed ride.
    Cached on the ride record (debrief_text column).
    """
    # Check cache
    if ride.debrief_text and not force:
        return {
            "debrief": ride.debrief_text,
            "generated_at": str(ride.debrief_generated_at),
            "cached": True,
        }

    context = _build_debrief_context(db, user, ride)

    try:
        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        response = client.messages.create(
            model=SONNET_MODEL,
            max_tokens=500,
            system=DEBRIEF_SYSTEM_PROMPT,
            messages=[{
                "role": "user",
                "content": f"Generate a post-ride debrief for this ride:\n\n```json\n{json.dumps(context, indent=2, default=str)}\n```",
            }],
        )
        debrief_text = response.content[0].text.strip()
    except Exception as e:
        logger.error(f"Debrief generation failed: {e}")
        rider_name = context["rider_name"]
        r = context["ride"]
        debrief_text = (
            f"Nice work out there, {rider_name}. "
            f"You logged {r['duration_minutes']} minutes"
        )
        if r.get("tss"):
            debrief_text += f" for {r['tss']:.0f} TSS"
        debrief_text += ". Every ride counts toward your goal — keep building."

    # Cache on ride
    ride.debrief_text = debrief_text
    ride.debrief_generated_at = datetime.utcnow()
    db.commit()

    return {
        "debrief": debrief_text,
        "generated_at": ride.debrief_generated_at.isoformat(),
        "cached": False,
    }


# ── Metric Explanation ───────────────────────────────────────────────────────

EXPLAIN_SYSTEM_PROMPT = """\
You are Coach Marco, explaining a cycling performance metric to a rider in \
their specific context. Make it personal and actionable.

Rules:
1. Address the rider by first name.
2. Explain what this metric means FOR THEM — not a generic definition.
3. Compare to benchmarks or their own history where relevant.
4. Suggest what to do about it (if applicable).
5. 2-4 sentences max. Be concise and conversational.
6. Return ONLY the explanation text. No JSON, no headings."""


def explain_metric(
    db: Session, user: User, metric_name: str, metric_value: float | str
) -> dict:
    """
    Generate a personalised explanation of a metric.
    No caching — these are cheap Haiku calls.
    """
    rider_name = (user.full_name or user.email.split("@")[0]).split()[0]
    fitness = get_current_fitness(db, user.id)

    context = {
        "rider_name": rider_name,
        "metric_name": metric_name,
        "metric_value": metric_value,
        "ftp": user.ftp,
        "weight_kg": user.weight_kg,
        "experience": user.experience_level,
        "fitness": {
            "ctl": round(fitness["ctl"], 1),
            "atl": round(fitness["atl"], 1),
            "tsb": round(fitness["tsb"], 1),
        },
    }

    try:
        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        response = client.messages.create(
            model=HAIKU_MODEL,
            max_tokens=200,
            system=EXPLAIN_SYSTEM_PROMPT,
            messages=[{
                "role": "user",
                "content": f"Explain this metric to the rider:\n\n```json\n{json.dumps(context, default=str)}\n```",
            }],
        )
        explanation = response.content[0].text.strip()
    except Exception as e:
        logger.error(f"Metric explanation failed: {e}")
        explanation = f"{rider_name}, your {metric_name} is currently {metric_value}. This reflects your recent training load and recovery balance."

    return {"explanation": explanation}
