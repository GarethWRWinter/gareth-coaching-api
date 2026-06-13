"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import Link from "next/link";
import {
  Calendar,
  ChevronLeft,
  ChevronRight,
  Plus,
  Download,
  Check,
  X,
  Trophy,
} from "lucide-react";
import { training, exports_, goals, users } from "@/lib/api";
import { formatDuration, formatDate, cn } from "@/lib/utils";
import { useAuth } from "@/lib/auth-context";
import type { Workout, GoalEvent } from "@/lib/api";

// Each workout renders as a full zone-colour block. The colour IS the intensity
// (warm earth scale, low→high), with text auto-contrasted per block.
const ZONE_STYLES: Record<
  string,
  { bg: string; fg: string; dark: boolean; label: string }
> = {
  recovery:   { bg: "#7C95A3", fg: "#FFFFFF", dark: true,  label: "Recovery · Z1" },
  endurance:  { bg: "#9FB295", fg: "#1C2A1C", dark: false, label: "Endurance · Z2" },
  tempo:      { bg: "#C7A458", fg: "#3A2E10", dark: false, label: "Tempo · Z3" },
  sweet_spot: { bg: "#C28F4E", fg: "#3A2A10", dark: false, label: "Sweet spot" },
  threshold:  { bg: "#C0714A", fg: "#FFFFFF", dark: true,  label: "Threshold · Z4" },
  vo2max:     { bg: "#B0573A", fg: "#FFFFFF", dark: true,  label: "VO₂ · Z5" },
  sprint:     { bg: "#95442E", fg: "#FFFFFF", dark: true,  label: "Sprint · Z6" },
  rest:       { bg: "#ECE8DE", fg: "#615B50", dark: false, label: "Rest" },
};

function getWeekDates(offset: number): { start: Date; dates: Date[] } {
  const today = new Date();
  const start = new Date(today);
  start.setDate(today.getDate() - today.getDay() + 1 + offset * 7); // Monday

  const dates = [];
  for (let i = 0; i < 7; i++) {
    const d = new Date(start);
    d.setDate(start.getDate() + i);
    dates.push(d);
  }
  return { start, dates };
}

function formatWeekDate(d: Date): string {
  return d.toISOString().split("T")[0];
}

export default function TrainingPage() {
  const queryClient = useQueryClient();
  const { user, refreshUser } = useAuth();
  const [weekOffset, setWeekOffset] = useState(0);
  const [showGenerate, setShowGenerate] = useState(false);
  const [genModel, setGenModel] = useState("traditional");
  const [showSchedule, setShowSchedule] = useState(false);
  const [hardDays, setHardDays] = useState<number[]>(
    user?.preferred_hard_days ?? []
  );
  const [restDays, setRestDays] = useState<number[]>(
    user?.rest_days ?? []
  );
  const [scheduleSaving, setScheduleSaving] = useState(false);

  const { start, dates } = getWeekDates(weekOffset);
  const weekStartStr = formatWeekDate(start);

  const { data: plans } = useQuery({
    queryKey: ["plans"],
    queryFn: () => training.getPlans(),
  });

  const { data: weekWorkouts, isLoading } = useQuery({
    queryKey: ["workouts-week", weekStartStr],
    queryFn: () => training.getWorkouts(undefined, weekStartStr),
  });

  const { data: goalsData } = useQuery({
    queryKey: ["goals"],
    queryFn: () => goals.list(),
  });

  const generateMutation = useMutation({
    mutationFn: (data: { periodization_model: string; goal_event_id?: string }) =>
      training.generatePlan(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["plans"] });
      queryClient.invalidateQueries({ queryKey: ["workouts-week"] });
      setShowGenerate(false);
    },
  });

  // Find the next upcoming goal (if any) — used to auto-link newly generated
  // plans to the goal so the plan peaks on race day.
  const nextUpcomingGoal = goalsData?.goals
    ?.filter((g) => g.status === "upcoming" && g.days_until != null && g.days_until >= 0)
    ?.sort((a, b) => (a.days_until ?? 0) - (b.days_until ?? 0))?.[0];

  const hasActivePlan =
    plans && plans.plans.filter((p) => p.status === "active").length > 0;

  const statusMutation = useMutation({
    mutationFn: ({ id, status }: { id: string; status: string }) =>
      training.updateWorkout(id, { status }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["workouts-week"] });
    },
  });

  // Group workouts by date
  const workoutsByDate: Record<string, Workout[]> = {};
  weekWorkouts?.forEach((w) => {
    const d = w.scheduled_date;
    if (!workoutsByDate[d]) workoutsByDate[d] = [];
    workoutsByDate[d].push(w);
  });

  // Group goal events by date
  const goalsByDate: Record<string, GoalEvent[]> = {};
  goalsData?.goals?.forEach((g) => {
    const d = g.event_date;
    if (!goalsByDate[d]) goalsByDate[d] = [];
    goalsByDate[d].push(g);
  });

  const today = new Date().toISOString().split("T")[0];
  const dayLabels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="font-display text-2xl font-light tracking-[-0.01em] text-vb-text">Training</h1>
          {hasActivePlan ? (
            <p className="mt-1 text-sm text-vb-text-dim">
              Active plan:{" "}
              {plans?.plans.find((p) => p.status === "active")?.name}
            </p>
          ) : (
            <p className="mt-1 text-sm text-vb-text-dim">No active plan</p>
          )}
        </div>
        <button
          onClick={() => setShowGenerate(!showGenerate)}
          className="flex items-center gap-2 rounded-sm bg-vb-forest px-4 py-2.5 text-sm font-medium text-white hover:bg-vb-forest-soft"
        >
          <Plus className="h-4 w-4" /> Generate Plan
        </button>
      </div>

      {/* Prompt: user has an upcoming goal but no active plan */}
      {!hasActivePlan && nextUpcomingGoal && !showGenerate && (
        <div className="rounded-md border border-vb-border-subtle border-l-[3px] border-l-vb-forest bg-vb-surface p-4 sm:p-5">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div className="flex items-start gap-3">
              <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-vb-sage-tint">
                <Trophy className="h-5 w-5 text-vb-forest" />
              </div>
              <div>
                <p className="text-sm font-medium text-vb-text">
                  Build a plan for {nextUpcomingGoal.event_name}
                </p>
                <p className="mt-1 text-xs text-vb-text-dim">
                  {formatDate(nextUpcomingGoal.event_date)}
                  {nextUpcomingGoal.days_until != null && nextUpcomingGoal.days_until > 0 && (
                    <> &middot; {nextUpcomingGoal.days_until} days away</>
                  )}
                  {" "}&middot; We&apos;ll create a periodised plan that peaks on race day.
                </p>
              </div>
            </div>
            <button
              onClick={() =>
                generateMutation.mutate({
                  periodization_model: "traditional",
                  // Let backend auto-detect primary goal from all upcoming goals
                })
              }
              disabled={generateMutation.isPending}
              className="rounded-sm bg-vb-forest px-4 py-2 text-sm font-medium text-white hover:bg-vb-forest-soft disabled:opacity-50"
            >
              {generateMutation.isPending ? "Generating..." : "Generate Plan"}
            </button>
          </div>
        </div>
      )}

      {/* Prompt: user has no active plan and no upcoming goal */}
      {!hasActivePlan && !nextUpcomingGoal && !showGenerate && (
        <div className="rounded-md border border-vb-border-subtle bg-vb-surface p-4 sm:p-5">
          <p className="text-sm font-medium text-vb-text">
            Ready to start training?
          </p>
          <p className="mt-1 text-xs text-vb-text-dim">
            Set a goal event first so your plan peaks on race day, or generate a
            generic 12-week plan to start building fitness now.
          </p>
          <div className="mt-3 flex flex-wrap gap-2">
            <Link
              href="/dashboard/goals"
              className="rounded-sm bg-vb-forest px-4 py-2 text-sm font-medium text-white hover:bg-vb-forest-soft"
            >
              Add a goal
            </Link>
            <button
              onClick={() => setShowGenerate(true)}
              className="rounded-sm border border-vb-border px-4 py-2 text-sm font-medium text-vb-forest hover:bg-vb-surface-raised"
            >
              Generate generic plan
            </button>
          </div>
        </div>
      )}

      {/* Generate Plan Dialog */}
      {showGenerate && (
        <div className="rounded-md border border-vb-border-subtle bg-vb-surface p-5">
          <h3 className="text-sm font-medium text-vb-text">
            Generate Training Plan
          </h3>
          <p className="mt-1 text-xs text-vb-text-dim">
            {nextUpcomingGoal
              ? `Creates a periodised plan peaking on ${nextUpcomingGoal.event_name} (${formatDate(nextUpcomingGoal.event_date)}).`
              : "Creates a 12-week periodised plan based on your profile."}
          </p>
          <div className="mt-4 flex flex-wrap items-end gap-3 sm:gap-4">
            <div className="min-w-[180px] flex-1">
              <label className="mb-1.5 block text-xs font-medium text-vb-text-dim">
                Periodization Model
              </label>
              <select
                value={genModel}
                onChange={(e) => setGenModel(e.target.value)}
                className="w-full rounded-sm border border-vb-border bg-vb-surface px-3 py-2 text-sm text-vb-text"
              >
                <option value="traditional">Traditional</option>
                <option value="polarized">Polarized</option>
                <option value="sweet_spot">Sweet Spot</option>
              </select>
            </div>
            <button
              onClick={() =>
                generateMutation.mutate({
                  periodization_model: genModel,
                  // Let backend auto-detect primary goal from all upcoming goals
                })
              }
              disabled={generateMutation.isPending}
              className="rounded-sm bg-vb-forest px-4 py-2 text-sm font-medium text-white hover:bg-vb-forest-soft disabled:opacity-50"
            >
              {generateMutation.isPending ? "Generating..." : "Generate"}
            </button>
            <button
              onClick={() => setShowGenerate(false)}
              className="rounded-sm border border-vb-border px-4 py-2 text-sm text-vb-forest hover:bg-vb-surface-raised"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* Training Schedule */}
      <div className="flex items-center gap-3">
        <button
          onClick={() => setShowSchedule(!showSchedule)}
          className="text-xs text-vb-text-dim hover:text-vb-forest transition-colors"
        >
          {showSchedule ? "Hide schedule" : "Adjust availability"}
        </button>
      </div>
      {showSchedule && (
        <div className="rounded-md border border-vb-border-subtle bg-vb-surface p-4">
          <p className="mb-3 text-xs text-vb-text-dim">
            Set your training schedule. Hard days get intensity sessions, rest days have no training. Click to cycle: Easy → Rest → Hard.
          </p>
          <div className="grid grid-cols-7 gap-2">
            {["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"].map((day, idx) => {
              const isHard = hardDays.includes(idx);
              const isRest = restDays.includes(idx);
              return (
                <div key={day} className="text-center">
                  <p className="mb-1 text-[10px] font-medium text-vb-text-muted">{day}</p>
                  <button
                    type="button"
                    onClick={() => {
                      if (isRest) {
                        setRestDays(restDays.filter(d => d !== idx));
                        setHardDays([...hardDays, idx]);
                      } else if (isHard) {
                        setHardDays(hardDays.filter(d => d !== idx));
                      } else {
                        setRestDays([...restDays, idx]);
                      }
                    }}
                    className={cn(
                      "w-full rounded-sm py-2 text-xs font-medium transition-colors",
                      isHard
                        ? "bg-vb-clay/15 text-vb-clay border border-vb-clay/40"
                        : isRest
                          ? "bg-vb-sunken text-vb-text-muted border border-vb-border-subtle"
                          : "bg-vb-sage-tint text-vb-forest border border-vb-forest/30"
                    )}
                  >
                    {isHard ? "Hard" : isRest ? "Rest" : "Easy"}
                  </button>
                </div>
              );
            })}
          </div>
          <div className="mt-3 flex items-center gap-2">
            <button
              onClick={async () => {
                setScheduleSaving(true);
                try {
                  await users.updateProfile({
                    preferred_hard_days: hardDays,
                    rest_days: restDays,
                  });
                  await refreshUser();
                  setShowSchedule(false);
                } finally {
                  setScheduleSaving(false);
                }
              }}
              disabled={scheduleSaving}
              className="rounded-sm bg-vb-forest px-3 py-1.5 text-xs font-medium text-white hover:bg-vb-forest-soft disabled:opacity-50"
            >
              {scheduleSaving ? "Saving..." : "Save Schedule"}
            </button>
            <p className="text-[10px] text-vb-text-muted">
              Re-generate your plan after saving to apply changes
            </p>
          </div>
        </div>
      )}

      {/* Week Navigation */}
      <div className="flex items-center justify-between">
        <button
          onClick={() => setWeekOffset((w) => w - 1)}
          className="rounded-sm border border-vb-border-subtle p-2 text-vb-text-dim hover:bg-vb-surface"
        >
          <ChevronLeft className="h-4 w-4" />
        </button>
        <div className="text-center">
          <p className="text-sm font-medium text-vb-text">
            {dates[0].toLocaleDateString("en-GB", {
              day: "numeric",
              month: "short",
            })}{" "}
            &ndash;{" "}
            {dates[6].toLocaleDateString("en-GB", {
              day: "numeric",
              month: "short",
              year: "numeric",
            })}
          </p>
          {weekOffset !== 0 && (
            <button
              onClick={() => setWeekOffset(0)}
              className="text-xs text-vb-forest hover:text-vb-forest-soft"
            >
              Back to this week
            </button>
          )}
        </div>
        <button
          onClick={() => setWeekOffset((w) => w + 1)}
          className="rounded-sm border border-vb-border-subtle p-2 text-vb-text-dim hover:bg-vb-surface"
        >
          <ChevronRight className="h-4 w-4" />
        </button>
      </div>

      {/* Week Grid */}
      <div className="-mx-4 overflow-x-auto px-4 pb-2 sm:mx-0 sm:px-0 sm:pb-0">
      <div className="grid min-w-[700px] grid-cols-7 gap-2 sm:min-w-0">
        {dates.map((date, i) => {
          const dateStr = formatWeekDate(date);
          const isToday = dateStr === today;
          const dayWorkouts = workoutsByDate[dateStr] || [];

          const dayGoals = goalsByDate[dateStr] || [];

          return (
            <div
              key={dateStr}
              className={cn(
                "min-h-[180px] rounded-md border p-3",
                isToday
                  ? "border-vb-forest bg-vb-sage-tint/40"
                  : "border-vb-border-subtle bg-vb-surface"
              )}
            >
              <div className="mb-2 flex items-center justify-between">
                <span
                  className={cn(
                    "text-xs font-medium",
                    isToday ? "text-vb-forest" : "text-vb-text-dim"
                  )}
                >
                  {dayLabels[i]}
                </span>
                <span
                  className={cn(
                    "text-xs tabular-nums",
                    isToday ? "text-vb-forest font-semibold" : "text-vb-text-muted"
                  )}
                >
                  {date.getDate()}
                </span>
              </div>

              <div className="space-y-1.5">
                {/* Goal events — displayed above workouts */}
                {dayGoals.map((goal) => (
                  <Link
                    key={goal.id}
                    href={`/dashboard/goals/${goal.id}`}
                    className="block rounded-sm border border-vb-border-subtle border-l-[3px] border-l-vb-clay bg-vb-surface p-2"
                  >
                    <div className="flex items-center gap-1.5">
                      <Trophy className="h-3 w-3 shrink-0 text-vb-clay" />
                      <p className="truncate text-xs font-medium text-vb-clay">
                        {goal.event_name}
                      </p>
                    </div>
                    <div className="mt-1 flex items-center gap-1.5">
                      <span className="rounded-sm bg-vb-clay/15 px-1 py-0.5 text-[9px] font-medium text-vb-clay">
                        {goal.priority.replace(/_/g, " ").toUpperCase()}
                      </span>
                      <span className="text-[10px] text-vb-text-muted">
                        {goal.event_type.replace(/_/g, " ")}
                      </span>
                    </div>
                  </Link>
                ))}

                {/* Workouts — full zone-colour blocks */}
                {dayWorkouts
                  .filter((w) => w.status !== "skipped")
                  .map((workout) => {
                    const hasActual = !!workout.actual_ride;
                    const score = workout.execution_score;
                    const z =
                      ZONE_STYLES[workout.workout_type] ?? ZONE_STYLES.rest;
                    const chipBg = z.dark
                      ? "rgba(255,255,255,0.22)"
                      : "rgba(0,0,0,0.08)";
                    return (
                      <div
                        key={workout.id}
                        className="rounded-md p-2.5"
                        style={{ backgroundColor: z.bg, color: z.fg }}
                      >
                        <Link
                          href={`/dashboard/training/${workout.id}`}
                          className="block"
                        >
                          <div className="flex items-start justify-between gap-1.5">
                            <div className="min-w-0">
                              <p
                                className="text-[10px] font-semibold uppercase tracking-[0.10em]"
                                style={{ opacity: 0.72 }}
                              >
                                {z.label}
                              </p>
                              <p className="mt-0.5 truncate text-[13px] font-medium leading-tight">
                                {workout.title}
                              </p>
                            </div>
                            {score != null && (
                              <span
                                className="shrink-0 rounded-sm px-1.5 py-0.5 text-[9px] font-semibold tabular-nums"
                                style={{ backgroundColor: chipBg }}
                              >
                                {score.toFixed(1)}
                              </span>
                            )}
                          </div>
                        </Link>

                        {/* Planned / actual stats */}
                        {!hasActual ? (
                          (workout.planned_duration_seconds ||
                            workout.planned_tss) && (
                            <p
                              className="mt-1.5 text-[11px] font-medium tabular-nums"
                              style={{ opacity: 0.85 }}
                            >
                              {workout.planned_duration_seconds
                                ? formatDuration(workout.planned_duration_seconds)
                                : ""}
                              {workout.planned_duration_seconds &&
                              workout.planned_tss
                                ? " · "
                                : ""}
                              {workout.planned_tss
                                ? `${Math.round(workout.planned_tss)} TSS`
                                : ""}
                            </p>
                          )
                        ) : (
                          <p
                            className="mt-1.5 text-[11px] font-medium tabular-nums"
                            style={{ opacity: 0.95 }}
                          >
                            ✓{" "}
                            {formatDuration(
                              workout.actual_ride!.moving_time_seconds ??
                                workout.actual_ride!.duration_seconds ??
                                0
                            )}
                            {workout.actual_ride!.tss != null
                              ? ` · ${Math.round(workout.actual_ride!.tss)} TSS`
                              : ""}
                          </p>
                        )}

                        {/* Status controls */}
                        {workout.status === "planned" && (
                          <div className="mt-2 flex gap-1.5">
                            <button
                              onClick={() =>
                                statusMutation.mutate({
                                  id: workout.id,
                                  status: "completed",
                                })
                              }
                              title="Mark completed"
                              className="flex h-[22px] w-[22px] items-center justify-center rounded-[5px]"
                              style={{ backgroundColor: chipBg, color: z.fg }}
                            >
                              <Check className="h-3 w-3" />
                            </button>
                            <button
                              onClick={() =>
                                statusMutation.mutate({
                                  id: workout.id,
                                  status: "skipped",
                                })
                              }
                              title="Skip"
                              className="flex h-[22px] w-[22px] items-center justify-center rounded-[5px]"
                              style={{ backgroundColor: chipBg, color: z.fg }}
                            >
                              <X className="h-3 w-3" />
                            </button>
                          </div>
                        )}
                        {workout.status === "completed" && !hasActual && (
                          <p
                            className="mt-1.5 text-[10px] font-medium"
                            style={{ opacity: 0.85 }}
                          >
                            Done ✓
                          </p>
                        )}
                      </div>
                    );
                  })}
                {dayWorkouts.filter((w) => w.status !== "skipped").length === 0 && dayGoals.length === 0 && (
                  <p className="py-2 text-center text-[10px] text-vb-text-muted">
                    Rest
                  </p>
                )}
              </div>
            </div>
          );
        })}
      </div>
      </div>

      {/* Plan Phases */}
      {plans &&
        plans.plans
          .filter((p) => p.status === "active")
          .slice(0, 1)
          .map((plan) => (
            <div
              key={plan.id}
              className="rounded-md border border-vb-border-subtle bg-vb-surface p-5"
            >
              <h2 className="mb-3 font-display text-lg font-light tracking-[-0.01em] text-vb-text">
                Plan Phases
              </h2>
              <div className="flex gap-1 overflow-x-auto">
                {plan.phases?.map((phase) => {
                  const isCurrentPhase =
                    today >= phase.start_date && today <= phase.end_date;
                  return (
                    <div
                      key={phase.id}
                      className={cn(
                        "flex-1 rounded-sm border p-3",
                        isCurrentPhase
                          ? "border-vb-forest bg-vb-sage-tint/40"
                          : "border-vb-border-subtle bg-vb-surface"
                      )}
                    >
                      <p className="text-xs font-semibold capitalize text-vb-text">
                        {phase.phase_type.replace("_", " ")}
                      </p>
                      <p className="mt-0.5 text-[10px] text-vb-text-dim">
                        {formatDate(phase.start_date)} &ndash;{" "}
                        {formatDate(phase.end_date)}
                      </p>
                      {phase.focus && (
                        <p className="mt-1 text-[10px] text-vb-text-muted">
                          {phase.focus}
                        </p>
                      )}
                      <p className="mt-1 text-[10px] tabular-nums text-vb-text-dim">
                        {phase.workout_count} workouts
                      </p>
                    </div>
                  );
                })}
              </div>
            </div>
          ))}
    </div>
  );
}
