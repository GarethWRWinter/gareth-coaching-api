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

const WORKOUT_COLORS: Record<string, string> = {
  recovery: "border-l-slate-400 bg-slate-800/30",
  endurance: "border-l-blue-400 bg-blue-900/10",
  tempo: "border-l-green-400 bg-green-900/10",
  sweet_spot: "border-l-yellow-400 bg-yellow-900/10",
  threshold: "border-l-orange-400 bg-orange-900/10",
  vo2max: "border-l-red-400 bg-red-900/10",
  sprint: "border-l-purple-400 bg-purple-900/10",
  rest: "border-l-slate-600 bg-slate-800/20",
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
    mutationFn: (data: { periodization_model: string }) =>
      training.generatePlan(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["plans"] });
      queryClient.invalidateQueries({ queryKey: ["workouts-week"] });
      setShowGenerate(false);
    },
  });

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
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Training</h1>
          {plans && plans.plans.filter((p) => p.status === "active").length > 0 ? (
            <p className="mt-1 text-sm text-slate-400">
              Active plan:{" "}
              {plans.plans.find((p) => p.status === "active")?.name}
            </p>
          ) : (
            <p className="mt-1 text-sm text-slate-400">No active plan</p>
          )}
        </div>
        <button
          onClick={() => setShowGenerate(!showGenerate)}
          className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-medium text-white hover:bg-blue-500"
        >
          <Plus className="h-4 w-4" /> Generate Plan
        </button>
      </div>

      {/* Generate Plan Dialog */}
      {showGenerate && (
        <div className="rounded-xl border border-slate-700 bg-slate-800 p-5">
          <h3 className="text-sm font-semibold text-white">
            Generate Training Plan
          </h3>
          <p className="mt-1 text-xs text-slate-400">
            Creates a 12-week periodized plan based on your profile
          </p>
          <div className="mt-4 flex items-end gap-4">
            <div className="flex-1">
              <label className="mb-1.5 block text-xs font-medium text-slate-300">
                Periodization Model
              </label>
              <select
                value={genModel}
                onChange={(e) => setGenModel(e.target.value)}
                className="w-full rounded-lg border border-slate-600 bg-slate-700 px-3 py-2 text-sm text-white"
              >
                <option value="traditional">Traditional</option>
                <option value="polarized">Polarized</option>
                <option value="sweet_spot">Sweet Spot</option>
              </select>
            </div>
            <button
              onClick={() =>
                generateMutation.mutate({ periodization_model: genModel })
              }
              disabled={generateMutation.isPending}
              className="rounded-lg bg-green-600 px-4 py-2 text-sm font-medium text-white hover:bg-green-500 disabled:opacity-50"
            >
              {generateMutation.isPending ? "Generating..." : "Generate"}
            </button>
            <button
              onClick={() => setShowGenerate(false)}
              className="rounded-lg border border-slate-600 px-4 py-2 text-sm text-slate-300 hover:bg-slate-700"
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
          className="text-xs text-slate-400 hover:text-white transition-colors"
        >
          {showSchedule ? "Hide schedule" : "Adjust availability"}
        </button>
      </div>
      {showSchedule && (
        <div className="rounded-xl border border-slate-700 bg-slate-800 p-4">
          <p className="mb-3 text-xs text-slate-400">
            Set your training schedule. Hard days get intensity sessions, rest days have no training. Click to cycle: Easy → Rest → Hard.
          </p>
          <div className="grid grid-cols-7 gap-2">
            {["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"].map((day, idx) => {
              const isHard = hardDays.includes(idx);
              const isRest = restDays.includes(idx);
              return (
                <div key={day} className="text-center">
                  <p className="mb-1 text-[10px] font-medium text-slate-500">{day}</p>
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
                      "w-full rounded-lg py-2 text-xs font-medium transition-colors",
                      isHard
                        ? "bg-orange-500/20 text-orange-400 border border-orange-500/40"
                        : isRest
                          ? "bg-slate-700/50 text-slate-500 border border-slate-600/30"
                          : "bg-blue-500/15 text-blue-400 border border-blue-500/30"
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
              className="rounded-lg bg-blue-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-blue-500 disabled:opacity-50"
            >
              {scheduleSaving ? "Saving..." : "Save Schedule"}
            </button>
            <p className="text-[10px] text-slate-500">
              Re-generate your plan after saving to apply changes
            </p>
          </div>
        </div>
      )}

      {/* Week Navigation */}
      <div className="flex items-center justify-between">
        <button
          onClick={() => setWeekOffset((w) => w - 1)}
          className="rounded-lg border border-slate-700 p-2 text-slate-300 hover:bg-slate-800"
        >
          <ChevronLeft className="h-4 w-4" />
        </button>
        <div className="text-center">
          <p className="text-sm font-medium text-white">
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
              className="text-xs text-blue-400 hover:text-blue-300"
            >
              Back to this week
            </button>
          )}
        </div>
        <button
          onClick={() => setWeekOffset((w) => w + 1)}
          className="rounded-lg border border-slate-700 p-2 text-slate-300 hover:bg-slate-800"
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
                "min-h-[180px] rounded-xl border p-3",
                isToday
                  ? "border-blue-500/50 bg-blue-900/10"
                  : "border-slate-800 bg-slate-800/30"
              )}
            >
              <div className="mb-2 flex items-center justify-between">
                <span
                  className={cn(
                    "text-xs font-medium",
                    isToday ? "text-blue-400" : "text-slate-400"
                  )}
                >
                  {dayLabels[i]}
                </span>
                <span
                  className={cn(
                    "text-xs",
                    isToday ? "text-blue-400 font-semibold" : "text-slate-500"
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
                    className="block rounded-lg border border-amber-500/50 bg-amber-900/20 p-2"
                  >
                    <div className="flex items-center gap-1.5">
                      <Trophy className="h-3 w-3 shrink-0 text-amber-400" />
                      <p className="truncate text-xs font-semibold text-amber-300">
                        {goal.event_name}
                      </p>
                    </div>
                    <div className="mt-1 flex items-center gap-1.5">
                      <span className="rounded bg-amber-700/40 px-1 py-0.5 text-[9px] font-medium text-amber-300">
                        {goal.priority.replace(/_/g, " ").toUpperCase()}
                      </span>
                      <span className="text-[10px] text-amber-400/70">
                        {goal.event_type.replace(/_/g, " ")}
                      </span>
                    </div>
                  </Link>
                ))}

                {/* Workouts */}
                {dayWorkouts
                  .filter((w) => w.status !== "skipped")
                  .map((workout) => (
                  <div
                    key={workout.id}
                    className={cn(
                      "rounded-lg border-l-2 p-2",
                      WORKOUT_COLORS[workout.workout_type] ||
                        "border-l-slate-500 bg-slate-800/30"
                    )}
                  >
                    <Link
                      href={`/dashboard/training/${workout.id}`}
                      className="block"
                    >
                      <p className="truncate text-xs font-medium text-white hover:text-blue-400">
                        {workout.title}
                      </p>
                    </Link>
                    {workout.description && (
                      <p className="mt-0.5 line-clamp-2 text-[10px] text-slate-500">
                        {workout.description}
                      </p>
                    )}
                    <div className="mt-1 flex items-center gap-1.5">
                      {workout.planned_duration_seconds && (
                        <span className="text-[10px] text-slate-400">
                          {formatDuration(workout.planned_duration_seconds)}
                        </span>
                      )}
                      {workout.planned_tss && (
                        <span className="text-[10px] text-slate-400">
                          {Math.round(workout.planned_tss)} TSS
                        </span>
                      )}
                    </div>
                    {/* Status buttons */}
                    <div className="mt-1.5 flex gap-1">
                      {workout.status === "planned" && (
                        <>
                          <button
                            onClick={() =>
                              statusMutation.mutate({
                                id: workout.id,
                                status: "completed",
                              })
                            }
                            className="rounded bg-green-700/30 p-0.5 text-green-400 hover:bg-green-700/50"
                            title="Mark completed"
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
                            className="rounded bg-slate-700/30 p-0.5 text-slate-400 hover:bg-slate-700/50"
                            title="Skip"
                          >
                            <X className="h-3 w-3" />
                          </button>
                        </>
                      )}
                      {workout.status === "completed" && (
                        <span className="text-[10px] text-green-400">
                          Done
                        </span>
                      )}
                    </div>
                  </div>
                ))}
                {dayWorkouts.filter((w) => w.status !== "skipped").length === 0 && dayGoals.length === 0 && (
                  <p className="py-2 text-center text-[10px] text-slate-600">
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
              className="rounded-xl border border-slate-800 bg-slate-800/50 p-5"
            >
              <h2 className="mb-3 text-lg font-semibold text-white">
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
                        "flex-1 rounded-lg border p-3",
                        isCurrentPhase
                          ? "border-blue-500 bg-blue-900/20"
                          : "border-slate-700 bg-slate-800/50"
                      )}
                    >
                      <p className="text-xs font-semibold capitalize text-white">
                        {phase.phase_type.replace("_", " ")}
                      </p>
                      <p className="mt-0.5 text-[10px] text-slate-400">
                        {formatDate(phase.start_date)} &ndash;{" "}
                        {formatDate(phase.end_date)}
                      </p>
                      {phase.focus && (
                        <p className="mt-1 text-[10px] text-slate-500">
                          {phase.focus}
                        </p>
                      )}
                      <p className="mt-1 text-[10px] text-slate-400">
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
