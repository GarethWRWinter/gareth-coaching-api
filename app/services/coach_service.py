"""
AI Coach service powered by Claude.

Assembles rider context, manages chat sessions, and streams
responses via Claude API with SSE.
"""

import base64
import json
import re
from datetime import date, datetime, timedelta, timezone

import anthropic
from sqlalchemy.orm import Session

from collections import Counter

from app.config import settings
from app.core.formulas import rider_profile_scores, rider_type_profile, w_per_kg as calc_w_per_kg
from app.models.chat import ChatMessage, ChatRole, ChatSession
from app.models.training import Workout, WorkoutStatus
from app.models.user import User
from app.services.metrics_service import (
    get_all_time_power_profile,
    get_current_fitness,
    get_ftp_history,
    get_pmc_data,
    get_weekly_training_load,
)
from app.services.onboarding_service import get_goals, get_onboarding_response
from app.services.plan_service import get_plans, get_workouts_by_date
from app.services.ride_service import get_rides
from app.services.zone_service import get_zones

# === System Prompt ===

COACH_SYSTEM_PROMPT = """You are Coach Marco — a world-class cycling performance director, sports scientist, and integrated life-performance partner. You bring the depth of a professional team coach with the warmth and accessibility of a trusted mentor.

## Who You Are

You've spent decades working with riders at every level — from weekend warriors to Grand Tour contenders. You combine the analytical rigour of sports science with the human understanding of a life coach. You don't just build faster cyclists; you help people build lives where cycling and performance thrive in harmony with everything else that matters to them.

You address the rider by their first name. You're direct but never cold. You ground every recommendation in the rider's actual data. You celebrate progress — however small — because consistency is what builds champions. You're occasionally witty, always honest, and you never talk down to anyone.

## Your Training Philosophy

Your coaching draws on the proven methodologies of the world's leading coaches and scientists. You don't follow a single dogma — you synthesise what works for each individual rider:

**Intensity Distribution (Dr. Stephen Seiler — Polarized Training)**
The research is clear: approximately 80% easy, 20% hard produces the best endurance adaptations. Most amateur riders fall into the "moderate intensity trap" — riding too hard on easy days and too easy on hard days. When the rider's zone distribution shows excessive Zone 3 time, flag this. True Zone 2 rides should feel almost embarrassingly easy. Hard days should be genuinely hard.

**Metabolic Foundation (Dr. Iñigo San Millán — Zone 2 Training)**
Zone 2 work builds the engine underneath everything — mitochondrial density, fat oxidation efficiency, lactate clearance capacity. This isn't junk miles; it's the most important work a cyclist does. Especially for riders building base fitness, in early periodization phases, or with low CTL, Zone 2 is the prescription. Think of it as investing — the returns compound over months and years.

**Periodization (Joe Friel — The Cyclist's Training Bible)**
Training follows a rhythm: base → build → peak → race → transition. Each phase has a purpose, and skipping phases creates fragile fitness. Match your advice to the rider's current training phase and experience level. Newer riders (lower training age) respond to simpler stimuli — they don't need complex interval structures. Experienced riders need more specificity and variation to continue adapting.

**Power-Based Training (Dr. Andrew Coggan & Tim Cusick)**
The rider's platform already calculates CTL, ATL, TSB, Normalized Power, IF, and TSS — these are Coggan's frameworks. Interpret these numbers with nuance, not alarm. A TSB of -15 during a build phase is normal and expected. A TSB of -15 during taper week is a problem. Use the Power Duration Curve to identify limiters — where is the rider strong relative to their FTP, and where do they fall off?

**Practical Application (Hunter Allen — Training & Racing with a Power Meter)**
Numbers on a screen mean nothing without translation into actionable workouts. When prescribing sessions, describe them clearly with power targets as % of FTP, duration, and recovery. When analysing rides, focus on what the data reveals about pacing, fueling, and tactical decisions.

**Marginal Gains (Tim Kerrison / Team Ineos)**
At every level, the integrated approach matters. Nutrition timing, sleep quality, heat adaptation, altitude considerations, equipment choices, even body position on the bike — everything contributes. When discussing race preparation or performance optimisation, think holistically. The biggest gains often come from the simplest changes: better sleep, consistent fueling, reducing life stress.

**Time-Crunched Training (Chris Carmichael / CTS)**
Many riders have limited time. When weekly hours available is under 8, focus on time-efficient protocols: sweet spot intervals (88-93% FTP), over-under threshold work, short VO2max blocks. Quality trumps quantity for time-limited athletes. Never make a rider feel guilty about their available time — work with what they have.

**Individualised Profiling (Neal Henderson / 4DP)**
Every rider has a unique phenotype. Use the rider's strengths and weaknesses from their profile to tailor advice. A natural sprinter needs different development than a climber. An all-rounder might benefit from specialising toward their goal event demands. The rider type, power profile scores, and specific strengths/weaknesses data in the context should drive individualisation.

## Mental Performance Coaching

Physical training is only half the equation. The mind drives the body, and you coach both.

**Managing the Inner Critic (Dr. Steve Peters — The Chimp Paradox)**
Every rider has an emotional brain (the "chimp") that reacts before the rational brain can intervene. Pre-race anxiety, mid-interval panic, frustration after a bad ride — these are the chimp talking. The key isn't to fight it but to acknowledge it and have a pre-prepared plan. When a rider expresses anxiety or self-doubt, help them:
- Recognise the emotion without judging it ("That anxiety is completely normal — it means you care")
- Separate the emotional reaction from the facts ("What does your data actually say?")
- Create action plans for predictable moments of doubt

**Building Confidence Through Data**
When a rider doubts themselves, the most powerful thing you can do is show them their own numbers. "Your CTL has grown from X to Y. Your FTP is up Z watts. You held threshold power for 20 minutes last Tuesday. The data says you're ready — trust the work you've done."

**Visualisation and Mental Rehearsal**
Before key workouts and races, guide riders through mental rehearsal. What does the course look like? Where are the hard moments? What does success feel like? How will they respond when it hurts? Riders who mentally rehearse perform measurably better.

**Process Over Outcome**
Help riders focus on what they can control — execution, effort, attitude — rather than results. A perfectly executed race that finishes 15th is more valuable for growth than a lucky podium. Set process goals alongside outcome goals.

**Resilience and Setbacks**
Bad races happen. Injuries happen. Life gets in the way. Normalise setbacks and help riders reframe them as data, not failure. "What can we learn from this? What would you do differently? How do we adjust going forward?"

## Life Coaching and Balance

You coach the whole person, not just the athlete. Cycling performance doesn't exist in a vacuum — it's intertwined with work, relationships, sleep, stress, and life satisfaction.

**Work-Training Balance**
Ask about work stress, travel, deadlines. Heavy work weeks require reduced training load — the body doesn't distinguish between sources of stress. When TSB is very negative but training load isn't particularly high, probe for life stressors. Help riders plan training around professional demands, not in spite of them.

**Relationships and Family**
Training affects partners, families, and friendships. Help riders communicate their cycling goals to the people who matter. Suggest strategies: shared calendars, involving family in events, being fully present when not training. Never position training as more important than relationships — the goal is harmony, not sacrifice. A rider with a supportive home environment trains better.

**Sleep as Performance**
Sleep is the number one recovery tool — more important than any supplement, compression garment, or recovery ride. When discussing recovery, always ask about sleep quality and quantity. 7-9 hours, consistent schedule, cool dark room. Poor sleep undermines every training adaptation.

**Career and Life Goals**
For amateur athletes, the career funds the cycling. Protect it. Help riders think about energy management across all life domains. Some weeks, the best training decision is a rest day and a focused work session. Help riders see cycling as part of a fulfilling life, not as an escape from one.

**Total Stress Load**
Training stress + work stress + family stress + financial stress = total load. Recovery capacity is finite. When a rider is dealing with a house move, a new baby, a job change, or relationship difficulties — acknowledge that training capacity is genuinely reduced. Adjust expectations without making the rider feel like they're failing.

**Motivation and Purpose**
When motivation dips, explore why — don't just push harder. Burnout, staleness, misaligned goals, life changes, loss of purpose. Sometimes the answer is a training break. Sometimes it's a new goal. Sometimes it's reconnecting with why they started cycling in the first place. Distinguish intrinsic motivation (love of riding) from extrinsic (results, Strava, comparison) and help nurture the former.

## Proactive Coaching Triggers

When you see concerning patterns in the rider's data or conversation, proactively address them:

- **Overtraining risk**: TSB below -25 → suggest recovery, probe for symptoms (fatigue, irritability, poor sleep, elevated resting HR)
- **High ramp rate**: CTL increasing >7 TSS/week → warn about injury and illness risk, suggest a recovery week
- **Low compliance**: <70% of planned workouts completed → explore barriers with curiosity, not judgment. Are the workouts too hard? Too long? Is life getting in the way?
- **FTP plateau**: No improvement in 8+ weeks → suggest an FTP test, a training approach change, or explore whether recovery/nutrition/sleep is the limiter
- **Excessive intensity**: Too many Zone 4-5 days without Zone 1-2 recovery → recommend easy days and explain why
- **Race approaching**: Event within 14 days → shift to taper advice, race-day planning, mental preparation, and pacing strategy
- **Life stress signals**: Rider mentions work pressure, relationship issues, poor sleep, or general fatigue → acknowledge impact and adjust training expectations
- **Motivation decline**: Shorter messages, less enthusiasm, avoiding training discussion → gently check in on how they're feeling about cycling and life in general
- **Phase transitions**: Moving between training phases → guide the rider through the psychological shift (e.g., base phase feels boring but it's building the engine)

## Boundaries

- **Medical**: You're not a doctor, and you'd never pretend to be one. For injuries, persistent pain, illness, or medical concerns, always recommend a sports medicine professional. But you can help think about how to structure training around recovery.
- **Nutrition**: For specific meal plans, calorie counting, or dietary protocols, a registered sports dietitian is the right resource. You can absolutely help with fueling strategy around workouts and races, hydration, and general nutrition principles for endurance athletes.
- **Mental Health**: For clinical anxiety, depression, disordered eating, or issues beyond normal training stress, a sports psychologist is the appropriate professional. You provide evidence-based mental performance coaching — visualisation, self-talk, goal-setting, confidence building, and race-day mindset.
- **Financial**: You don't provide financial advice, but you can help riders think about how to budget time and energy for training alongside other life priorities.

## Modifying the Training Plan

You have tools to modify the rider's training plan directly. Use them when the conversation leads to agreed changes:

- **update_workout**: Change a workout's title, description, type, date, duration, or TSS. Use the workout IDs from the `this_week` context.
- **swap_workout_date**: Swap the dates of two workouts to rearrange the week.
- **add_workout**: Add a new session to the plan.
- **skip_workout**: Mark a workout as skipped.

**When to use tools:**
- The rider asks to change their plan ("Can we swap Tuesday and Thursday?", "I want to skip tomorrow's session", "Add a recovery ride on Friday")
- You recommend a change and the rider agrees ("Let's do that", "Sounds good, make the change")
- Always confirm with the rider before making changes — describe what you'll do, then act

**When NOT to use tools:**
- General discussion about training philosophy or future plans
- The rider is just asking questions, not requesting changes
- Changes that affect weeks beyond the current week (explain you can only modify this week's plan)

**After using a tool**, briefly confirm what was changed and explain how it fits the overall training plan.

## Post-Event Debrief

When a rider has recently completed a goal event, proactively offer to debrief:
- Acknowledge the achievement — completing an event matters regardless of result
- Analyse their self-assessment alongside the actual ride data
- Compare planned vs actual: pacing, power fade, nutrition
- Connect the result to the training block — what worked in preparation?
- Identify 2-3 actionable takeaways for next time
- Discuss recovery plan and what's next
- Process disappointment constructively — it's data, not failure

## Response Format

- Keep responses concise and actionable unless the rider asks for a deep dive
- Use the rider's actual numbers from context — never speak in vague generalities
- When prescribing workouts, describe them clearly with power targets as % of FTP, duration, recovery intervals, and the purpose of the session
- Ask clarifying questions before prescribing when the situation is ambiguous
- When a rider is struggling, lead with empathy before solutions
- Use analogies and stories to make training concepts tangible
"""


def _build_rider_context(db: Session, user: User) -> str:
    """
    Build a comprehensive context snapshot of the rider's current state.

    This is injected into each message as context for the AI coach.
    Sections are ordered logically: who → wants → current state → history → plan → events.
    Each section is wrapped in try/except so a failure in one doesn't break the rest.
    """
    context: dict = {}
    today = date.today()

    # ── 1. Profile (enriched with physical data) ──
    profile: dict = {
        "name": user.full_name or "Rider",
        "ftp": user.ftp,
        "weight_kg": user.weight_kg,
        "experience": user.experience_level,
        "equipment": {
            "power_meter": user.has_power_meter,
            "smart_trainer": user.has_smart_trainer,
            "hr_monitor": user.has_hr_monitor,
        },
        "weekly_hours": user.weekly_hours_available,
    }
    if user.height_cm:
        profile["height_cm"] = user.height_cm
    if user.max_hr:
        profile["max_hr"] = user.max_hr
    if user.resting_hr:
        profile["resting_hr"] = user.resting_hr
    if user.date_of_birth:
        try:
            dob = user.date_of_birth
            if hasattr(dob, "date"):
                dob = dob.date()
            profile["age"] = today.year - dob.year - (
                (today.month, today.day) < (dob.month, dob.day)
            )
        except Exception:
            pass
    context["profile"] = profile

    # ── 2. Onboarding context (goals & motivation) ──
    try:
        onboarding = get_onboarding_response(db, user.id)
        if onboarding:
            ob: dict = {"primary_goal": onboarding.primary_goal}
            if onboarding.secondary_goals:
                ob["secondary_goals"] = onboarding.secondary_goals
            if onboarding.years_cycling:
                ob["years_cycling"] = onboarding.years_cycling
            if onboarding.indoor_outdoor_preference:
                ob["indoor_outdoor"] = onboarding.indoor_outdoor_preference
            context["onboarding"] = ob
    except Exception:
        pass

    # ── 3-5. Fitness + Power Profile + Profile Scores ──
    # Combined to avoid calling the expensive get_all_time_power_profile() twice.
    ftp = user.ftp or 0
    weight = user.weight_kg or 0

    try:
        fitness = get_current_fitness(db, user.id)

        # Power profile (expensive query — call once, reuse everywhere)
        power_profile_raw: dict = {}
        try:
            power_profile_raw = get_all_time_power_profile(db, user.id)
        except Exception:
            pass

        power_values = {d: v["best_power"] for d, v in power_profile_raw.items()}

        # Rider type profiling
        rider_profile = {"type": "unknown", "strengths": [], "weaknesses": []}
        if ftp > 0 and weight > 0:
            rider_profile = rider_type_profile(power_values, ftp, weight)

        # Profile scores (radar chart, 0-100 per energy system)
        profile_scores: dict = {}
        if weight > 0:
            profile_scores = rider_profile_scores(power_values, weight)

        # Fitness level classification
        ctl = fitness["ctl"]
        fitness_level = (
            "untrained" if ctl < 20 else
            "fair" if ctl < 40 else
            "moderate" if ctl < 60 else
            "good" if ctl < 80 else
            "very_good" if ctl < 100 else
            "excellent"
        )

        context["fitness"] = {
            "ctl": fitness["ctl"],
            "atl": fitness["atl"],
            "tsb": fitness["tsb"],
            "ramp_rate": fitness["ramp_rate"],
            "w_per_kg": round(calc_w_per_kg(ftp, weight), 2) if ftp and weight else None,
            "rider_type": rider_profile["type"],
            "strengths": rider_profile["strengths"],
            "weaknesses": rider_profile["weaknesses"],
            "fitness_level": fitness_level,
        }

        # Profile scores (Section H)
        if profile_scores:
            context["profile_scores"] = profile_scores

        # Power profile with best efforts (Section B)
        if power_profile_raw:
            duration_labels = {
                5: "5s", 10: "10s", 15: "15s", 30: "30s", 60: "1min",
                120: "2min", 300: "5min", 600: "10min", 1200: "20min",
                1800: "30min", 3600: "60min", 5400: "90min",
            }
            context["power_profile"] = {
                duration_labels.get(d, f"{d}s"): {
                    k: v for k, v in {
                        "watts": round(entry["best_power"]),
                        "w_per_kg": round(entry["best_power"] / weight, 2) if weight > 0 else None,
                        "date": str(entry["ride_date"]) if entry.get("ride_date") else None,
                    }.items() if v is not None
                }
                for d, entry in sorted(power_profile_raw.items())
                if entry["best_power"] > 0
            }

    except Exception:
        context["fitness"] = {"ctl": 0, "atl": 0, "tsb": 0}

    # ── 6. Power Zones ──
    try:
        zones = get_zones(user)
        if zones.get("power_zones"):
            context["power_zones"] = zones["power_zones"]
    except Exception:
        pass

    # ── 7. FTP History (progression over time) ──
    try:
        ftp_hist = get_ftp_history(db, user.id)
        if ftp_hist:
            context["ftp_history"] = [
                {"date": str(h["date"]), "ftp": h["ftp"]}
                for h in ftp_hist
            ]
    except Exception:
        pass

    # ── 8. Weekly Training Load (last 8 weeks) ──
    try:
        weekly = get_weekly_training_load(db, user.id, weeks=8)
        if weekly:
            context["weekly_load"] = [
                {
                    "week": str(w["week_start"]),
                    "tss": round(w["total_tss"]),
                    "rides": w["ride_count"],
                    "hours": round(w["total_duration_seconds"] / 3600, 1) if w["total_duration_seconds"] else 0,
                    "avg_if": w["avg_intensity_factor"],
                }
                for w in weekly
            ]
    except Exception:
        pass

    # ── 9. Training Compliance ──
    try:
        past_workouts = (
            db.query(Workout)
            .filter(
                Workout.user_id == user.id,
                Workout.scheduled_date <= today,
            )
            .all()
        )
        if past_workouts:
            total = len(past_workouts)
            status_counts = Counter(str(w.status) for w in past_workouts)
            completed = status_counts.get(WorkoutStatus.completed, 0) + status_counts.get("completed", 0)
            skipped = status_counts.get(WorkoutStatus.skipped, 0) + status_counts.get("skipped", 0)

            compliance_rate = round(completed / total * 100) if total > 0 else 0

            # Per-type compliance
            type_stats: dict = {}
            for w in past_workouts:
                wtype = str(w.workout_type)
                if wtype not in type_stats:
                    type_stats[wtype] = {"total": 0, "completed": 0}
                type_stats[wtype]["total"] += 1
                if str(w.status) in ("completed", "WorkoutStatus.completed"):
                    type_stats[wtype]["completed"] += 1

            type_compliance = {
                t: round(s["completed"] / s["total"] * 100)
                for t, s in type_stats.items()
                if s["total"] >= 2  # Only types with enough data
            }

            context["compliance"] = {
                "overall_pct": compliance_rate,
                "completed": completed,
                "skipped": skipped,
                "total_planned": total,
                "by_type": type_compliance,
            }
    except Exception:
        pass

    # ── 10. Training Plan + Current Phase ──
    try:
        plans = get_plans(db, user.id)
        active_plans = [p for p in plans if p.status == "active"]
        if active_plans:
            plan = active_plans[0]
            context["training_plan"] = {
                "name": plan.name,
                "start_date": str(plan.start_date),
                "end_date": str(plan.end_date),
                "model": plan.periodization_model,
            }

            # Current phase
            for phase in plan.phases:
                if phase.start_date <= today <= phase.end_date:
                    context["current_phase"] = {
                        "type": phase.phase_type,
                        "focus": phase.focus,
                        "start": str(phase.start_date),
                        "end": str(phase.end_date),
                    }
                    break
    except Exception:
        pass

    # ── 11. This Week's Workouts ──
    try:
        week_start = today - timedelta(days=today.weekday())  # Monday
        workouts = get_workouts_by_date(db, user.id, week_start=week_start)
        if workouts:
            context["this_week"] = [
                {
                    "id": w.id,
                    "date": str(w.scheduled_date),
                    "title": w.title,
                    "type": w.workout_type,
                    "description": w.description,
                    "status": w.status,
                    "planned_tss": w.planned_tss,
                    "planned_duration_min": round(w.planned_duration_seconds / 60) if w.planned_duration_seconds else None,
                }
                for w in workouts[:7]
            ]
    except Exception:
        pass

    # ── 12. Recent Rides (last 15) ──
    try:
        rides, _ = get_rides(db, user.id, page=1, per_page=15)
        if rides:
            context["recent_rides"] = [
                {
                    k: v for k, v in {
                        "date": str(r.ride_date.date() if hasattr(r.ride_date, "date") else r.ride_date),
                        "title": r.title,
                        "duration_min": round(r.duration_seconds / 60) if r.duration_seconds else None,
                        "tss": round(r.tss, 1) if r.tss else None,
                        "np": round(r.normalized_power) if r.normalized_power else None,
                        "if": round(r.intensity_factor, 2) if r.intensity_factor else None,
                        "distance_km": round(r.distance_meters / 1000, 1) if r.distance_meters else None,
                        "elevation_m": round(r.elevation_gain_meters) if r.elevation_gain_meters else None,
                        "avg_hr": r.average_hr,
                        "workout_id": r.workout_id,
                    }.items() if v is not None
                }
                for r in rides
            ]
    except Exception:
        pass

    # ── 13. Goal Events ──
    try:
        user_goals = get_goals(db, user.id)
        if user_goals:
            context["goal_events"] = []
            for g in user_goals:
                goal_info: dict = {
                    "event_name": g.event_name,
                    "event_date": str(g.event_date),
                    "event_type": g.event_type,
                    "priority": g.priority,
                }
                if g.event_date >= today:
                    goal_info["days_until"] = (g.event_date - today).days
                # Assessment data for completed goals
                if hasattr(g, "status") and g.status and g.status != "upcoming":
                    goal_info["status"] = g.status
                    if g.finish_time_seconds:
                        goal_info["finish_time_seconds"] = g.finish_time_seconds
                    if g.overall_satisfaction:
                        goal_info["overall_satisfaction"] = g.overall_satisfaction
                    if g.perceived_exertion:
                        goal_info["perceived_exertion"] = g.perceived_exertion
                    if g.assessment_data:
                        ad = g.assessment_data if isinstance(g.assessment_data, dict) else {}
                        if ad.get("went_well"):
                            goal_info["went_well"] = ad["went_well"]
                        if ad.get("to_improve"):
                            goal_info["to_improve"] = ad["to_improve"]
                    # Include actual ride metrics if linked
                    if g.actual_ride_id and hasattr(g, "actual_ride") and g.actual_ride:
                        ride = g.actual_ride
                        ride_info: dict = {}
                        if ride.normalized_power:
                            ride_info["np"] = round(ride.normalized_power)
                        if ride.intensity_factor:
                            ride_info["if"] = round(ride.intensity_factor, 2)
                        if ride.variability_index:
                            ride_info["vi"] = round(ride.variability_index, 2)
                        if ride.tss:
                            ride_info["tss"] = round(ride.tss, 1)
                        if ride_info:
                            goal_info["actual_ride_metrics"] = ride_info
                if g.target_duration_minutes:
                    goal_info["target_duration_minutes"] = g.target_duration_minutes
                if g.notes:
                    goal_info["notes"] = g.notes
                if g.route_url:
                    goal_info["route_url"] = g.route_url
                if g.route_data:
                    # Include route summary but exclude the full elevation profile
                    # (too large for coach context — hundreds of trackpoints)
                    rd = g.route_data if isinstance(g.route_data, dict) else {}
                    goal_info["route_data"] = {
                        k: v for k, v in rd.items()
                        if k != "elevation_profile"
                    }
                context["goal_events"].append(goal_info)
    except Exception:
        pass

    return json.dumps(context, indent=2, default=str)


# === Coach Tools (Claude tool_use) ===

COACH_TOOLS = [
    {
        "name": "update_workout",
        "description": "Update an existing workout's title, description, type, date, duration, or TSS. Use this when the rider and coach agree to modify a planned workout — e.g. changing a threshold session to an endurance ride, adjusting duration, or rewriting the description.",
        "input_schema": {
            "type": "object",
            "properties": {
                "workout_id": {
                    "type": "string",
                    "description": "The ID of the workout to update (from this_week context)",
                },
                "title": {"type": "string", "description": "New workout title"},
                "description": {"type": "string", "description": "New workout description explaining purpose and how to perform it"},
                "workout_type": {
                    "type": "string",
                    "enum": ["endurance", "tempo", "sweet_spot", "threshold", "vo2max", "sprint", "recovery", "rest"],
                    "description": "New workout type",
                },
                "scheduled_date": {"type": "string", "description": "New date in YYYY-MM-DD format"},
                "planned_duration_seconds": {"type": "integer", "description": "New planned duration in seconds"},
                "planned_tss": {"type": "number", "description": "New planned TSS"},
            },
            "required": ["workout_id"],
        },
    },
    {
        "name": "swap_workout_date",
        "description": "Swap the scheduled dates of two workouts. Use when the rider wants to rearrange their week — e.g. moving Tuesday's intervals to Thursday.",
        "input_schema": {
            "type": "object",
            "properties": {
                "workout_id_a": {"type": "string", "description": "First workout ID"},
                "workout_id_b": {"type": "string", "description": "Second workout ID"},
            },
            "required": ["workout_id_a", "workout_id_b"],
        },
    },
    {
        "name": "add_workout",
        "description": "Add a new workout to the rider's plan. Use when the coach prescribes an additional session — e.g. adding a recovery ride or an extra interval session.",
        "input_schema": {
            "type": "object",
            "properties": {
                "scheduled_date": {"type": "string", "description": "Date in YYYY-MM-DD format"},
                "title": {"type": "string", "description": "Workout title"},
                "description": {"type": "string", "description": "Description of purpose and how to perform the workout"},
                "workout_type": {
                    "type": "string",
                    "enum": ["endurance", "tempo", "sweet_spot", "threshold", "vo2max", "sprint", "recovery", "rest"],
                },
                "planned_duration_seconds": {"type": "integer", "description": "Duration in seconds"},
                "planned_tss": {"type": "number", "description": "Estimated TSS"},
            },
            "required": ["scheduled_date", "title", "workout_type"],
        },
    },
    {
        "name": "skip_workout",
        "description": "Mark a workout as skipped. Use when the rider and coach agree to drop a session — due to fatigue, time constraints, or plan adjustment.",
        "input_schema": {
            "type": "object",
            "properties": {
                "workout_id": {"type": "string", "description": "The workout ID to skip"},
            },
            "required": ["workout_id"],
        },
    },
]


def _execute_tool(db: Session, user: User, tool_name: str, tool_input: dict) -> str:
    """
    Execute a coach tool and return a result string for Claude.

    Each tool modifies the training plan in the database and returns
    a confirmation message that Claude uses in its follow-up response.
    """
    if tool_name == "update_workout":
        workout = (
            db.query(Workout)
            .filter(Workout.id == tool_input["workout_id"], Workout.user_id == user.id)
            .first()
        )
        if not workout:
            return "Error: Workout not found."

        if "title" in tool_input:
            workout.title = tool_input["title"]
        if "description" in tool_input:
            workout.description = tool_input["description"]
        if "workout_type" in tool_input:
            workout.workout_type = tool_input["workout_type"]
        if "scheduled_date" in tool_input:
            workout.scheduled_date = date.fromisoformat(tool_input["scheduled_date"])
        if "planned_duration_seconds" in tool_input:
            workout.planned_duration_seconds = tool_input["planned_duration_seconds"]
        if "planned_tss" in tool_input:
            workout.planned_tss = tool_input["planned_tss"]

        workout.status = WorkoutStatus.modified
        db.commit()
        return f"Updated workout '{workout.title}' on {workout.scheduled_date}."

    elif tool_name == "swap_workout_date":
        wa = (
            db.query(Workout)
            .filter(Workout.id == tool_input["workout_id_a"], Workout.user_id == user.id)
            .first()
        )
        wb = (
            db.query(Workout)
            .filter(Workout.id == tool_input["workout_id_b"], Workout.user_id == user.id)
            .first()
        )
        if not wa or not wb:
            return "Error: One or both workouts not found."

        wa.scheduled_date, wb.scheduled_date = wb.scheduled_date, wa.scheduled_date
        db.commit()
        return f"Swapped dates: '{wa.title}' now on {wa.scheduled_date}, '{wb.title}' now on {wb.scheduled_date}."

    elif tool_name == "add_workout":
        workout = Workout(
            user_id=user.id,
            scheduled_date=date.fromisoformat(tool_input["scheduled_date"]),
            title=tool_input["title"],
            description=tool_input.get("description"),
            workout_type=tool_input["workout_type"],
            planned_duration_seconds=tool_input.get("planned_duration_seconds"),
            planned_tss=tool_input.get("planned_tss"),
            status=WorkoutStatus.planned,
        )
        db.add(workout)
        db.commit()
        db.refresh(workout)
        return f"Added workout '{workout.title}' on {workout.scheduled_date} (ID: {workout.id})."

    elif tool_name == "skip_workout":
        workout = (
            db.query(Workout)
            .filter(Workout.id == tool_input["workout_id"], Workout.user_id == user.id)
            .first()
        )
        if not workout:
            return "Error: Workout not found."

        workout.status = WorkoutStatus.skipped
        db.commit()
        return f"Skipped workout '{workout.title}' on {workout.scheduled_date}."

    return f"Error: Unknown tool '{tool_name}'."


# === Chat Session Management ===

def create_session(db: Session, user_id: str, title: str | None = None) -> ChatSession:
    """Create a new chat session."""
    session = ChatSession(
        user_id=user_id,
        title=title or f"Chat - {datetime.now(timezone.utc).strftime('%d %b %Y')}",
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def get_sessions(db: Session, user_id: str) -> list[ChatSession]:
    """Get all chat sessions for a user."""
    return (
        db.query(ChatSession)
        .filter(ChatSession.user_id == user_id)
        .order_by(ChatSession.created_at.desc())
        .all()
    )


def get_session(db: Session, session_id: str, user_id: str) -> ChatSession | None:
    """Get a single chat session with messages."""
    return (
        db.query(ChatSession)
        .filter(ChatSession.id == session_id, ChatSession.user_id == user_id)
        .first()
    )


def add_user_message(db: Session, session: ChatSession, content: str) -> ChatMessage:
    """Add a user message to a session."""
    message = ChatMessage(
        session_id=session.id,
        role=ChatRole.user,
        content=content,
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def add_assistant_message(
    db: Session, session: ChatSession, content: str,
    context_snapshot: dict | None = None, tokens_used: int | None = None,
) -> ChatMessage:
    """Add an assistant message to a session."""
    message = ChatMessage(
        session_id=session.id,
        role=ChatRole.assistant,
        content=content,
        context_snapshot=context_snapshot,
        tokens_used=tokens_used,
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


# === Claude API Integration ===

def _build_messages(session: ChatSession, max_messages: int = 20) -> list[dict]:
    """Build messages list for Claude API from chat history."""
    messages = sorted(session.messages, key=lambda m: m.created_at)

    # Take last N messages
    recent = messages[-max_messages:] if len(messages) > max_messages else messages

    return [
        {"role": msg.role, "content": msg.content}
        for msg in recent
    ]


async def stream_response(
    db: Session, user: User, session: ChatSession, user_message: str
):
    """
    Send message to Claude and stream response back with tool use support.

    Implements an agentic loop: when Claude calls a tool, we execute it,
    send the result back, and let Claude continue streaming its follow-up.

    Yields SSE-formatted chunks:
        data: {"type": "text", "content": "..."}
        data: {"type": "plan_updated"}   -- signals frontend to refresh training data
        data: {"type": "done"}
    """
    # Save user message
    add_user_message(db, session, user_message)

    # Build context
    rider_context = _build_rider_context(db, user)

    # Build system prompt with rider context
    system = f"""{COACH_SYSTEM_PROMPT}

## Current Rider Context
```json
{rider_context}
```

Today's date: {date.today().isoformat()}
"""

    # Build message history
    messages = _build_messages(session)

    # Stream from Claude with agentic tool loop
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    full_response = ""
    tokens_used = 0
    plan_was_updated = False

    try:
        # Agentic loop — keeps going while Claude wants to call tools
        max_iterations = 5
        for _ in range(max_iterations):
            with client.messages.stream(
                model="claude-sonnet-4-20250514",
                max_tokens=2048,
                system=system,
                messages=messages,
                tools=COACH_TOOLS,
            ) as stream:
                for event in stream:
                    if event.type == "content_block_delta":
                        if hasattr(event.delta, "text"):
                            full_response += event.delta.text
                            yield f'data: {json.dumps({"type": "text", "content": event.delta.text})}\n\n'

                final = stream.get_final_message()
                tokens_used += (
                    final.usage.input_tokens + final.usage.output_tokens
                    if final.usage else 0
                )

            # Check if Claude wants to use tools
            tool_use_blocks = [
                block for block in final.content
                if block.type == "tool_use"
            ]

            if not tool_use_blocks or final.stop_reason != "tool_use":
                # No tool calls — we're done
                break

            # Execute tool calls and build tool_result messages
            # Append assistant message with all content blocks
            messages.append({"role": "assistant", "content": final.content})

            tool_results = []
            for tool_block in tool_use_blocks:
                result_text = _execute_tool(
                    db, user, tool_block.name, tool_block.input
                )
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_block.id,
                    "content": result_text,
                })
                plan_was_updated = True

            messages.append({"role": "user", "content": tool_results})

            # Signal frontend that training plan was modified
            yield f'data: {json.dumps({"type": "plan_updated"})}\n\n'

            # Loop continues — Claude will respond to the tool results

    except anthropic.APIError as e:
        error_msg = f"Sorry, I'm having trouble connecting right now. Error: {str(e)}"
        full_response = error_msg
        yield f'data: {json.dumps({"type": "text", "content": error_msg})}\n\n'

    # Save assistant response
    context_snapshot = json.loads(rider_context) if rider_context else None
    add_assistant_message(db, session, full_response, context_snapshot, tokens_used)

    # Final plan_updated signal if tools were used (in case frontend missed it)
    if plan_was_updated:
        yield f'data: {json.dumps({"type": "plan_updated"})}\n\n'

    yield f'data: {json.dumps({"type": "done"})}\n\n'


VOICE_MODE_ADDENDUM = """
## Voice Mode Instructions
You are speaking out loud to the rider. Adjust your style:
- Keep responses conversational and concise — aim for 3-5 sentences unless they ask for detail
- Avoid markdown formatting, bullet points, numbered lists, and code blocks
- Use natural spoken language with contractions ("you're", "don't", "let's")
- Keep sentences short and clear — they will be read aloud
- Don't use special characters like asterisks, hashtags, or brackets
- Use "about" instead of precise decimals when speaking numbers
- It's fine to be warm and casual — you're having a conversation, not writing an essay
"""

# Regex for detecting sentence boundaries in streamed text
_SENTENCE_END = re.compile(r'[.!?]\s+|[.!?]$')


async def stream_voice_response(
    db: Session, user: User, session: ChatSession, user_message: str
):
    """
    Stream both text and audio responses via SSE with tool use support.

    Pipeline:
    1. Stream text from Claude (with agentic tool loop)
    2. Accumulate into sentences
    3. For each complete sentence, convert to audio via ElevenLabs
    4. Yield both text chunks and base64-encoded audio chunks

    SSE event types:
        data: {"type": "text", "content": "..."}
        data: {"type": "audio", "content": "<base64>", "sentence_index": N}
        data: {"type": "plan_updated"}
        data: {"type": "done"}

    Gracefully degrades — if ElevenLabs fails, text still streams normally.
    """
    from app.services.voice_service import is_voice_enabled, text_to_speech

    # Save user message
    add_user_message(db, session, user_message)

    # Build context
    rider_context = _build_rider_context(db, user)

    # Build system prompt with voice mode addendum
    system = f"""{COACH_SYSTEM_PROMPT}
{VOICE_MODE_ADDENDUM}

## Current Rider Context
```json
{rider_context}
```

Today's date: {date.today().isoformat()}
"""

    # Build message history
    messages = _build_messages(session)

    # Stream from Claude
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    full_response = ""
    sentence_buffer = ""
    sentence_index = 0
    tokens_used = 0
    voice_enabled = is_voice_enabled()
    plan_was_updated = False

    try:
        # Agentic loop — keeps going while Claude wants to call tools
        max_iterations = 5
        for _ in range(max_iterations):
            with client.messages.stream(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,  # Shorter for voice — conciseness matters
                system=system,
                messages=messages,
                tools=COACH_TOOLS,
            ) as stream:
                for event in stream:
                    if event.type == "content_block_delta":
                        if hasattr(event.delta, "text"):
                            text = event.delta.text
                            full_response += text
                            sentence_buffer += text

                            # Yield text chunk
                            yield f'data: {json.dumps({"type": "text", "content": text})}\n\n'

                            # Check for complete sentences and convert to audio
                            if voice_enabled:
                                while _SENTENCE_END.search(sentence_buffer):
                                    match = _SENTENCE_END.search(sentence_buffer)
                                    end_pos = match.end()
                                    complete_sentence = sentence_buffer[:end_pos].strip()
                                    sentence_buffer = sentence_buffer[end_pos:]

                                    if complete_sentence and len(complete_sentence) > 5:
                                        try:
                                            audio_bytes = await text_to_speech(
                                                complete_sentence
                                            )
                                            audio_b64 = base64.b64encode(
                                                audio_bytes
                                            ).decode("utf-8")
                                            yield f'data: {json.dumps({"type": "audio", "content": audio_b64, "sentence_index": sentence_index})}\n\n'
                                            sentence_index += 1
                                        except Exception:
                                            pass

                final = stream.get_final_message()
                tokens_used += (
                    final.usage.input_tokens + final.usage.output_tokens
                    if final.usage else 0
                )

            # Check if Claude wants to use tools
            tool_use_blocks = [
                block for block in final.content
                if block.type == "tool_use"
            ]

            if not tool_use_blocks or final.stop_reason != "tool_use":
                break

            # Execute tool calls
            messages.append({"role": "assistant", "content": final.content})

            tool_results = []
            for tool_block in tool_use_blocks:
                result_text = _execute_tool(
                    db, user, tool_block.name, tool_block.input
                )
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_block.id,
                    "content": result_text,
                })
                plan_was_updated = True

            messages.append({"role": "user", "content": tool_results})
            yield f'data: {json.dumps({"type": "plan_updated"})}\n\n'

        # Handle any remaining text in buffer
        if voice_enabled and sentence_buffer.strip() and len(
            sentence_buffer.strip()
        ) > 5:
            try:
                audio_bytes = await text_to_speech(
                    sentence_buffer.strip()
                )
                audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
                yield f'data: {json.dumps({"type": "audio", "content": audio_b64, "sentence_index": sentence_index})}\n\n'
            except Exception:
                pass

    except anthropic.APIError as e:
        error_msg = "Sorry, I'm having trouble connecting right now."
        full_response = error_msg
        yield f'data: {json.dumps({"type": "text", "content": error_msg})}\n\n'

    # Save assistant response
    context_snapshot = json.loads(rider_context) if rider_context else None
    add_assistant_message(db, session, full_response, context_snapshot, tokens_used)

    if plan_was_updated:
        yield f'data: {json.dumps({"type": "plan_updated"})}\n\n'

    yield f'data: {json.dumps({"type": "done"})}\n\n'


def get_non_streaming_response(
    db: Session, user: User, session: ChatSession, user_message: str
) -> str:
    """
    Non-streaming version for simpler integrations.
    Returns the full response text.
    """
    add_user_message(db, session, user_message)

    rider_context = _build_rider_context(db, user)

    system = f"""{COACH_SYSTEM_PROMPT}

## Current Rider Context
```json
{rider_context}
```

Today's date: {date.today().isoformat()}
"""

    messages = _build_messages(session)

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2048,
        system=system,
        messages=messages,
    )

    content = response.content[0].text
    tokens_used = (
        response.usage.input_tokens + response.usage.output_tokens
        if response.usage else 0
    )

    context_snapshot = json.loads(rider_context) if rider_context else None
    add_assistant_message(db, session, content, context_snapshot, tokens_used)

    return content
