"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { useState, useRef, useEffect, useMemo } from "react";
import {
  ArrowLeft,
  Calendar,
  Clock,
  Target,
  MapPin,
  Mountain,
  ExternalLink,
  Pencil,
  Trash2,
  Upload,
  MessageCircle,
  Zap,
  TrendingUp,
  Activity,
  X,
  Trophy,
  ClipboardCheck,
  Star,
} from "lucide-react";
import { goals as goalsApi, metrics, training, rides } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { cn, formatDate } from "@/lib/utils";
import { StatCard } from "@/components/ui/stat-card";
import { ElevationProfileChart } from "@/components/charts/elevation-profile-chart";
import { PerformanceCards } from "@/components/race-projection/performance-cards";
import { FitnessTrajectoryChart } from "@/components/charts/fitness-trajectory-chart";
import type { GoalEvent } from "@/lib/api";

const EVENT_TYPES = [
  { value: "road_race", label: "Road Race" },
  { value: "crit", label: "Criterium" },
  { value: "time_trial", label: "Time Trial" },
  { value: "gran_fondo", label: "Gran Fondo" },
  { value: "sportive", label: "Sportive" },
  { value: "gravel", label: "Gravel" },
  { value: "mtb", label: "MTB" },
  { value: "hill_climb", label: "Hill Climb" },
  { value: "stage_race", label: "Stage Race" },
  { value: "charity_ride", label: "Charity Ride" },
  { value: "century", label: "Century" },
];

const PRIORITIES = [
  { value: "a_race", label: "A Race (Primary)" },
  { value: "b_race", label: "B Race (Secondary)" },
  { value: "c_race", label: "C Race (Low Priority)" },
];

function formatDurationMinutes(minutes: number): string {
  const h = Math.floor(minutes / 60);
  const m = minutes % 60;
  if (h > 0) return m > 0 ? `${h}h ${m}m` : `${h}h`;
  return `${m}m`;
}

function priorityColor(priority: string): string {
  switch (priority) {
    case "a_race":
      return "bg-red-500/10 text-red-400 border-red-500/20";
    case "b_race":
      return "bg-yellow-500/10 text-yellow-400 border-yellow-500/20";
    case "c_race":
      return "bg-slate-500/10 text-slate-400 border-slate-500/20";
    default:
      return "bg-slate-500/10 text-slate-400 border-slate-500/20";
  }
}

function readinessColor(label: string): string {
  switch (label) {
    case "On Track":
      return "text-green-400";
    case "Needs Work":
      return "text-yellow-400";
    case "At Risk":
      return "text-red-400";
    default:
      return "text-slate-400";
  }
}

export default function GoalDetailPage() {
  const params = useParams();
  const router = useRouter();
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const goalId = params.id as string;
  const gpxInputRef = useRef<HTMLInputElement>(null);

  const [showEdit, setShowEdit] = useState(false);
  const [editForm, setEditForm] = useState({
    event_name: "",
    event_date: "",
    event_type: "road_race",
    priority: "a_race",
    target_duration_minutes: "",
    notes: "",
    route_url: "",
  });

  const { data: goal, isLoading } = useQuery({
    queryKey: ["goal", goalId],
    queryFn: () => goalsApi.get(goalId),
  });

  const { data: readiness } = useQuery({
    queryKey: ["goal-readiness", goalId],
    queryFn: () => goalsApi.getReadiness(goalId),
    enabled: !!goal && goal.days_until != null && goal.days_until > 0,
    retry: false,
  });

  const { data: fitness } = useQuery({
    queryKey: ["fitness-summary-quick"],
    queryFn: () => metrics.getFitnessSummary(false),
  });

  const { data: projection } = useQuery({
    queryKey: ["race-projection", goalId],
    queryFn: () => goalsApi.getRaceProjection(goalId),
    enabled:
      !!goal?.route_data?.elevation_profile &&
      goal.route_data.elevation_profile.length > 0,
    retry: false,
  });

  // Fetch actual ride data for completed goals with route data
  const { data: actualRideData } = useQuery({
    queryKey: ["ride-data", goal?.actual_ride_id],
    queryFn: () => rides.getData(goal!.actual_ride_id!, "30s"),
    enabled: !!goal?.actual_ride_id && (goal?.route_data?.elevation_profile?.length ?? 0) > 0,
  });

  const actualForChart = useMemo(() => {
    if (!actualRideData?.data_points) return undefined;
    return actualRideData.data_points
      .filter((dp) => dp.distance != null)
      .map((dp) => ({
        distance_km: dp.distance! / 1000,
        power: dp.power,
        speed: dp.speed ? dp.speed * 3.6 : null, // m/s → km/h
      }));
  }, [actualRideData]);

  const [showTargetPower, setShowTargetPower] = useState(true);
  const [showActualPower, setShowActualPower] = useState(true);

  const updateGoal = useMutation({
    mutationFn: () => {
      const data: Record<string, unknown> = {
        event_name: editForm.event_name,
        event_date: editForm.event_date,
        event_type: editForm.event_type,
        priority: editForm.priority,
      };
      if (editForm.target_duration_minutes) {
        data.target_duration_minutes = parseInt(editForm.target_duration_minutes);
      } else {
        data.target_duration_minutes = null;
      }
      data.notes = editForm.notes || null;
      data.route_url = editForm.route_url || null;
      return goalsApi.update(goalId, data as Parameters<typeof goalsApi.update>[1]);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["goal", goalId] });
      queryClient.invalidateQueries({ queryKey: ["goals"] });
      setShowEdit(false);
    },
  });

  const deleteGoalMutation = useMutation({
    mutationFn: () => goalsApi.delete(goalId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["goals"] });
      router.push("/dashboard/goals");
    },
  });

  const uploadGpx = useMutation({
    mutationFn: (file: File) => goalsApi.uploadGpx(goalId, file),
    onSuccess: (data) => {
      // Set the cache directly with the response (which now includes parsed route_data)
      queryClient.setQueryData(["goal", goalId], data);
      queryClient.invalidateQueries({ queryKey: ["goals"] });
    },
  });

  const generatePlan = useMutation({
    mutationFn: () =>
      training.generatePlan({ goal_event_id: goalId }),
    onSuccess: () => {
      router.push("/dashboard/training");
    },
  });

  const deleteGpx = useMutation({
    mutationFn: () => goalsApi.deleteGpx(goalId),
    onSuccess: (data) => {
      queryClient.setQueryData(["goal", goalId], data);
      queryClient.invalidateQueries({ queryKey: ["goals"] });
    },
  });

  const reparseGpx = useMutation({
    mutationFn: () => goalsApi.reparseGpx(goalId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["goal", goalId] });
    },
  });

  const refetchRoute = useMutation({
    mutationFn: () => goalsApi.refetchRoute(goalId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["goal", goalId] });
    },
  });

  // Auto-reparse GPX if file exists but elevation profile is missing
  const [autoRefreshed, setAutoRefreshed] = useState(false);
  useEffect(() => {
    if (!goal || autoRefreshed) return;

    // Case 1: GPX file exists but elevation profile is missing → reparse
    if (
      goal.gpx_file_path &&
      (!goal.route_data?.elevation_profile ||
        goal.route_data.elevation_profile.length === 0) &&
      !reparseGpx.isPending
    ) {
      setAutoRefreshed(true);
      reparseGpx.mutate();
      return;
    }

    // Case 2: Route URL exists but route_data is missing distance/elevation → refetch
    if (
      goal.route_url &&
      !goal.gpx_file_path &&
      goal.route_data &&
      !goal.route_data.total_distance_km &&
      !refetchRoute.isPending
    ) {
      setAutoRefreshed(true);
      refetchRoute.mutate();
      return;
    }
  }, [goal, autoRefreshed, reparseGpx.isPending, refetchRoute.isPending]);

  function openEdit() {
    if (!goal) return;
    setEditForm({
      event_name: goal.event_name,
      event_date: goal.event_date,
      event_type: goal.event_type,
      priority: goal.priority,
      target_duration_minutes: goal.target_duration_minutes?.toString() || "",
      notes: goal.notes || "",
      route_url: goal.route_url || "",
    });
    setShowEdit(true);
  }

  function buildCoachMessage(): string {
    if (!goal) return "";
    const parts = [
      `I'd like your help preparing for ${goal.event_name} on ${formatDate(goal.event_date)}.`,
      `It's a ${goal.event_type.replace(/_/g, " ")} (${goal.priority.replace(/_/g, " ")}).`,
    ];
    if (goal.route_data && !goal.route_data.error) {
      if (goal.route_data.total_distance_km) {
        parts.push(`The route is ${goal.route_data.total_distance_km}km`);
      }
      if (goal.route_data.elevation_gain_m) {
        parts.push(`with ${goal.route_data.elevation_gain_m}m of climbing.`);
      }
    }
    if (goal.target_duration_minutes) {
      parts.push(
        `My target duration is ${formatDurationMinutes(goal.target_duration_minutes)}.`
      );
    }
    if (goal.days_until != null && goal.days_until > 0) {
      parts.push(`I have ${goal.days_until} days to prepare.`);
    }
    parts.push("What should my preparation look like?");
    return parts.join(" ");
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-blue-500 border-t-transparent" />
      </div>
    );
  }

  if (!goal) {
    return (
      <div className="py-20 text-center text-slate-400">Goal not found</div>
    );
  }

  const inputClasses =
    "w-full rounded border border-slate-600 bg-slate-700 px-2.5 py-1.5 text-sm text-white focus:border-blue-500 focus:outline-none";

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <Link
            href="/dashboard/goals"
            className="mb-2 inline-flex items-center gap-1 text-sm text-slate-400 hover:text-white"
          >
            <ArrowLeft className="h-4 w-4" /> Back to goals
          </Link>
          <h1 className="text-2xl font-bold text-white">{goal.event_name}</h1>
          <div className="mt-1.5 flex flex-wrap items-center gap-2">
            <span className="inline-flex items-center gap-1 text-sm text-slate-400">
              <Calendar className="h-4 w-4" />
              {formatDate(goal.event_date)}
            </span>
            {goal.days_until != null && goal.days_until >= 0 && (
              <span className="rounded-full bg-blue-600/10 px-2.5 py-0.5 text-xs font-medium text-blue-400">
                {goal.days_until === 0
                  ? "Today!"
                  : `${goal.days_until} days away`}
              </span>
            )}
            <span className="inline-flex items-center rounded border px-2 py-0.5 text-xs capitalize">
              {goal.event_type.replace(/_/g, " ")}
            </span>
            <span
              className={`inline-flex items-center rounded border px-2 py-0.5 text-xs capitalize ${priorityColor(goal.priority)}`}
            >
              {goal.priority.replace(/_/g, " ")}
            </span>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={openEdit}
            className="flex items-center gap-1.5 rounded-lg border border-slate-700 px-3 py-2 text-sm text-slate-300 hover:bg-slate-800"
          >
            <Pencil className="h-4 w-4" /> Edit
          </button>
          <button
            onClick={() => {
              if (confirm(`Delete "${goal.event_name}"?`)) {
                deleteGoalMutation.mutate();
              }
            }}
            className="flex items-center gap-1.5 rounded-lg border border-red-900/50 px-3 py-2 text-sm text-red-400 hover:bg-red-950/50"
          >
            <Trash2 className="h-4 w-4" /> Delete
          </button>
        </div>
      </div>

      {/* Assessment Banner — needs assessment */}
      {goal.needs_assessment && (
        <Link
          href={`/dashboard/goals/${goalId}/assess`}
          className="flex items-center gap-4 rounded-xl border-2 border-amber-500/50 bg-amber-900/10 p-5 transition-colors hover:border-amber-500/80 hover:bg-amber-900/20"
        >
          <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-amber-500/20">
            <ClipboardCheck className="h-6 w-6 text-amber-400" />
          </div>
          <div className="flex-1">
            <p className="text-base font-semibold text-amber-300">
              How did {goal.event_name} go?
            </p>
            <p className="mt-0.5 text-sm text-amber-400/70">
              Complete your race report — capture results, link your ride data, and debrief with Coach Marco.
            </p>
          </div>
          <span className="rounded-lg bg-amber-600 px-4 py-2 text-sm font-medium text-white">
            Race Report
          </span>
        </Link>
      )}

      {/* Assessment Results — completed goals */}
      {goal.assessment_completed_at && (
        <div className="space-y-4">
          {/* Result Summary Card */}
          <div className="rounded-xl border border-slate-800 bg-slate-800/50 p-5">
            <div className="flex items-center justify-between">
              <h2 className="flex items-center gap-2 text-lg font-semibold text-white">
                <Trophy className="h-5 w-5 text-amber-400" />
                Result
              </h2>
              <span className={`rounded-full px-3 py-1 text-xs font-semibold uppercase ${
                goal.status === "completed"
                  ? "bg-green-500/15 text-green-400"
                  : goal.status === "dnf"
                    ? "bg-amber-500/15 text-amber-400"
                    : "bg-red-500/15 text-red-400"
              }`}>
                {goal.status === "dns" ? "DNS" : goal.status === "dnf" ? "DNF" : "Completed"}
              </span>
            </div>
            <div className="mt-4 grid grid-cols-2 gap-4 sm:grid-cols-4">
              {goal.finish_time_seconds && (
                <div className="rounded-lg border border-slate-700 bg-slate-700/30 p-3">
                  <p className="text-xs text-slate-400">Finish Time</p>
                  <p className="text-lg font-bold text-white">
                    {Math.floor(goal.finish_time_seconds / 3600)}h{" "}
                    {Math.floor((goal.finish_time_seconds % 3600) / 60)}m{" "}
                    {goal.finish_time_seconds % 60}s
                  </p>
                </div>
              )}
              {goal.finish_position && (
                <div className="rounded-lg border border-slate-700 bg-slate-700/30 p-3">
                  <p className="text-xs text-slate-400">Position</p>
                  <p className="text-lg font-bold text-white">
                    {goal.finish_position}
                    {goal.finish_position_total && (
                      <span className="text-sm text-slate-400">/{goal.finish_position_total}</span>
                    )}
                  </p>
                </div>
              )}
              {goal.overall_satisfaction && (
                <div className="rounded-lg border border-slate-700 bg-slate-700/30 p-3">
                  <p className="text-xs text-slate-400">Satisfaction</p>
                  <p className="flex items-center gap-1 text-lg font-bold text-white">
                    {goal.overall_satisfaction}
                    <span className="text-sm text-slate-400">/10</span>
                    <Star className="h-4 w-4 text-amber-400" />
                  </p>
                </div>
              )}
              {goal.perceived_exertion && (
                <div className="rounded-lg border border-slate-700 bg-slate-700/30 p-3">
                  <p className="text-xs text-slate-400">RPE</p>
                  <p className="text-lg font-bold text-white">
                    {goal.perceived_exertion}
                    <span className="text-sm text-slate-400">/10</span>
                  </p>
                </div>
              )}
            </div>

            {/* Takeaways */}
            {goal.assessment_data && (() => {
              const ad = goal.assessment_data as Record<string, unknown>;
              return (
                <div className="mt-4 grid gap-3 sm:grid-cols-2">
                  {ad.went_well ? (
                    <div className="rounded-lg border border-green-800/50 bg-green-900/10 p-3">
                      <p className="text-xs font-medium text-green-400">What went well</p>
                      <p className="mt-1 text-sm text-slate-300">
                        {String(ad.went_well)}
                      </p>
                    </div>
                  ) : null}
                  {ad.to_improve ? (
                    <div className="rounded-lg border border-amber-800/50 bg-amber-900/10 p-3">
                      <p className="text-xs font-medium text-amber-400">To improve</p>
                      <p className="mt-1 text-sm text-slate-300">
                        {String(ad.to_improve)}
                      </p>
                    </div>
                  ) : null}
                </div>
              );
            })()}
          </div>
        </div>
      )}

      {/* Edit Form */}
      {showEdit && (
        <div className="rounded-xl border border-slate-700 bg-slate-800/50 p-5">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-lg font-semibold text-white">Edit Goal</h2>
            <button
              onClick={() => setShowEdit(false)}
              className="rounded p-1 text-slate-400 hover:text-white"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <label className="mb-1 block text-xs font-medium text-slate-400">
                Event Name
              </label>
              <input
                value={editForm.event_name}
                onChange={(e) =>
                  setEditForm({ ...editForm, event_name: e.target.value })
                }
                className={inputClasses}
              />
            </div>
            <div>
              <label className="mb-1 block text-xs font-medium text-slate-400">
                Date
              </label>
              <input
                type="date"
                value={editForm.event_date}
                onChange={(e) =>
                  setEditForm({ ...editForm, event_date: e.target.value })
                }
                className={inputClasses}
              />
            </div>
            <div>
              <label className="mb-1 block text-xs font-medium text-slate-400">
                Type
              </label>
              <select
                value={editForm.event_type}
                onChange={(e) =>
                  setEditForm({ ...editForm, event_type: e.target.value })
                }
                className={inputClasses}
              >
                {EVENT_TYPES.map((t) => (
                  <option key={t.value} value={t.value}>
                    {t.label}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="mb-1 block text-xs font-medium text-slate-400">
                Priority
              </label>
              <select
                value={editForm.priority}
                onChange={(e) =>
                  setEditForm({ ...editForm, priority: e.target.value })
                }
                className={inputClasses}
              >
                {PRIORITIES.map((p) => (
                  <option key={p.value} value={p.value}>
                    {p.label}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="mb-1 block text-xs font-medium text-slate-400">
                Target Duration (min)
              </label>
              <input
                type="number"
                value={editForm.target_duration_minutes}
                onChange={(e) =>
                  setEditForm({
                    ...editForm,
                    target_duration_minutes: e.target.value,
                  })
                }
                placeholder="e.g. 240"
                className={inputClasses}
              />
            </div>
            <div>
              <label className="mb-1 block text-xs font-medium text-slate-400">
                Route URL
              </label>
              <input
                type="url"
                value={editForm.route_url}
                onChange={(e) =>
                  setEditForm({ ...editForm, route_url: e.target.value })
                }
                className={inputClasses}
              />
            </div>
          </div>
          <div className="mt-4">
            <label className="mb-1 block text-xs font-medium text-slate-400">
              Notes
            </label>
            <textarea
              value={editForm.notes}
              onChange={(e) =>
                setEditForm({ ...editForm, notes: e.target.value })
              }
              rows={3}
              className={`${inputClasses} resize-none`}
            />
          </div>
          <div className="mt-4 flex gap-2">
            <button
              onClick={() => updateGoal.mutate()}
              disabled={!editForm.event_name || !editForm.event_date || updateGoal.isPending}
              className="rounded-lg bg-green-600 px-4 py-2 text-sm font-medium text-white hover:bg-green-500 disabled:opacity-50"
            >
              {updateGoal.isPending ? "Saving..." : "Save Changes"}
            </button>
            <button
              onClick={() => setShowEdit(false)}
              className="rounded-lg border border-slate-600 px-4 py-2 text-sm text-slate-300 hover:bg-slate-700"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* Stats Row */}
      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        {goal.target_duration_minutes && (
          <StatCard
            label="Target Duration"
            value={formatDurationMinutes(goal.target_duration_minutes)}
          />
        )}
        {goal.days_until != null && goal.days_until > 0 && (
          <StatCard
            label="Days Until"
            value={goal.days_until}
            unit="days"
          />
        )}
        {goal.route_data?.total_distance_km && (
          <StatCard
            label="Distance"
            value={goal.route_data.total_distance_km}
            unit="km"
          />
        )}
        {goal.route_data?.elevation_gain_m && (
          <StatCard
            label="Elevation"
            value={Math.round(goal.route_data.elevation_gain_m)}
            unit="m"
          />
        )}
      </div>

      {/* Race Day Projection */}
      {projection && (
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <Target className="h-5 w-5 text-emerald-400" />
            <h2 className="text-lg font-semibold text-white">Race Day Projection</h2>
          </div>
          <PerformanceCards projection={projection} daysUntil={goal.days_until} />
          {projection.fitness_trajectory.length > 2 && (
            <div className="rounded-xl border border-slate-800 bg-slate-800/50 p-4">
              <p className="mb-2 text-xs font-medium uppercase text-slate-400">
                Fitness Trajectory
              </p>
              <FitnessTrajectoryChart trajectory={projection.fitness_trajectory} />
            </div>
          )}
        </div>
      )}

      {/* Course Profile — elevation chart or GPX upload CTA */}
      {goal.route_data?.elevation_profile &&
        goal.route_data.elevation_profile.length > 0 ? (
          <div className="rounded-xl border border-slate-800 bg-slate-800/50 p-5">
            <div className="mb-3 flex items-center justify-between">
              <p className="text-xs font-medium uppercase text-slate-400">
                Course Profile
                {goal.gpx_file_path && (
                  <span className="ml-2 inline-flex items-center gap-1 rounded bg-green-500/15 px-1.5 py-0.5 text-[10px] font-medium normal-case text-green-400">
                    <Mountain className="h-2.5 w-2.5" /> GPX
                  </span>
                )}
              </p>
              <div className="flex items-center gap-1.5">
                <button
                  onClick={() => gpxInputRef.current?.click()}
                  disabled={uploadGpx.isPending}
                  className="flex items-center gap-1 rounded-lg border border-slate-700 px-2.5 py-1 text-xs text-slate-400 hover:border-blue-500 hover:text-blue-400"
                >
                  <Upload className="h-3 w-3" />
                  {uploadGpx.isPending ? "Uploading..." : "Replace GPX"}
                </button>
                {goal.gpx_file_path && (
                  <button
                    onClick={() => {
                      if (confirm("Remove GPX file and route data? This will clear the elevation profile and pacing analysis.")) {
                        deleteGpx.mutate();
                      }
                    }}
                    disabled={deleteGpx.isPending}
                    className="flex items-center gap-1 rounded-lg border border-red-900/50 px-2.5 py-1 text-xs text-red-400 hover:bg-red-950/50"
                  >
                    <Trash2 className="h-3 w-3" />
                    {deleteGpx.isPending ? "Removing..." : "Remove"}
                  </button>
                )}
              </div>
            </div>
            {/* Toggle pills when actual ride data is available */}
            {actualForChart && actualForChart.length > 0 && (
              <div className="mb-3 flex flex-wrap items-center gap-2">
                <span className="text-[10px] uppercase text-slate-500 mr-1">Show:</span>
                {projection?.pacing_strategy && (
                  <button
                    onClick={() => setShowTargetPower((v) => !v)}
                    className={cn(
                      "rounded-full px-3 py-1 text-xs font-medium transition-colors",
                      showTargetPower
                        ? "bg-amber-500/20 text-amber-400 border border-amber-500/40"
                        : "bg-slate-700/50 text-slate-500 border border-slate-700"
                    )}
                  >
                    Target Power {showTargetPower ? "✓" : ""}
                  </button>
                )}
                <button
                  onClick={() => setShowActualPower((v) => !v)}
                  className={cn(
                    "rounded-full px-3 py-1 text-xs font-medium transition-colors",
                    showActualPower
                      ? "bg-red-500/20 text-red-400 border border-red-500/40"
                      : "bg-slate-700/50 text-slate-500 border border-slate-700"
                  )}
                >
                  Actual Power {showActualPower ? "✓" : ""}
                </button>
              </div>
            )}
            <ElevationProfileChart
              data={goal.route_data.elevation_profile}
              pacingStrategy={projection?.pacing_strategy}
              actualRideData={actualForChart}
              showTargetPower={showTargetPower}
              showActualPower={showActualPower}
            />
          </div>
        ) : (
          <div className="rounded-xl border border-dashed border-slate-700 bg-slate-800/30 p-5">
            <input
              ref={gpxInputRef}
              type="file"
              accept=".gpx"
              className="hidden"
              onChange={(e) => {
                const file = e.target.files?.[0];
                if (file) uploadGpx.mutate(file);
                e.target.value = "";
              }}
            />
            <div className="flex flex-col items-center gap-3 py-4 text-center">
              <div className="flex h-12 w-12 items-center justify-center rounded-full bg-slate-700/50">
                <Mountain className="h-6 w-6 text-green-400" />
              </div>
              <div>
                <p className="text-sm font-medium text-slate-200">
                  {goal.gpx_file_path
                    ? "Re-upload GPX to update the elevation profile"
                    : "Upload a GPX file for the elevation profile"}
                </p>
                <p className="mx-auto mt-1 max-w-sm text-xs text-slate-500">
                  {goal.route_data?.source === "strava"
                    ? "Strava provides summary stats. Upload a GPX export for the full course profile."
                    : "Export the route from Strava, RideWithGPS, or Komoot as a .gpx file"}
                </p>
              </div>
              <button
                onClick={() => gpxInputRef.current?.click()}
                disabled={uploadGpx.isPending}
                className="flex w-full items-center justify-center gap-2 rounded-lg bg-green-600 px-6 py-3 text-sm font-medium text-white hover:bg-green-500 disabled:opacity-50 sm:w-auto"
              >
                <Upload className="h-4 w-4" />
                {uploadGpx.isPending ? "Uploading..." : "Upload GPX File"}
              </button>
            </div>
          </div>
        )}

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Route & Event Details */}
        <div className="rounded-xl border border-slate-800 bg-slate-800/50 p-5">
          <h2 className="mb-4 text-lg font-semibold text-white">
            Event Details
          </h2>

          <div className="space-y-3">
            {/* Route data */}
            {goal.route_data && !goal.route_data.error && (
              <div className="rounded-lg border border-slate-700 bg-slate-700/30 p-3">
                <div className="flex items-center justify-between">
                  <p className="text-xs font-medium uppercase text-slate-400">
                    Route Info
                  </p>
                  {goal.route_data.source && (
                    <span className="rounded bg-slate-600/50 px-1.5 py-0.5 text-[10px] capitalize text-slate-400">
                      {goal.route_data.source}
                    </span>
                  )}
                </div>
                {(goal.route_data.title || goal.route_data.name) && (
                  <p className="mt-1.5 text-sm font-medium text-white">
                    {goal.route_data.title || goal.route_data.name}
                  </p>
                )}
                {goal.route_data.description && (
                  <p className="mt-1 text-xs text-slate-400">
                    {goal.route_data.description}
                  </p>
                )}
                {(goal.route_data.total_distance_km || goal.route_data.elevation_gain_m) && (
                  <div className="mt-2 grid grid-cols-2 gap-3">
                    {goal.route_data.total_distance_km && (
                      <div className="flex items-center gap-2">
                        <MapPin className="h-4 w-4 text-blue-400" />
                        <div>
                          <p className="text-sm font-medium text-white">
                            {goal.route_data.total_distance_km}km
                          </p>
                          <p className="text-xs text-slate-500">Distance</p>
                        </div>
                      </div>
                    )}
                    {goal.route_data.elevation_gain_m && (
                      <div className="flex items-center gap-2">
                        <Mountain className="h-4 w-4 text-green-400" />
                        <div>
                          <p className="text-sm font-medium text-white">
                            {goal.route_data.elevation_gain_m}m
                          </p>
                          <p className="text-xs text-slate-500">Climbing</p>
                        </div>
                      </div>
                    )}
                    {goal.route_data.avg_gradient_pct != null && (
                      <div className="flex items-center gap-2">
                        <TrendingUp className="h-4 w-4 text-yellow-400" />
                        <div>
                          <p className="text-sm font-medium text-white">
                            {goal.route_data.avg_gradient_pct}%
                          </p>
                          <p className="text-xs text-slate-500">Avg gradient</p>
                        </div>
                      </div>
                    )}
                    {goal.route_data.max_elevation_m != null && (
                      <div>
                        <p className="text-sm font-medium text-white">
                          {goal.route_data.max_elevation_m}m
                        </p>
                        <p className="text-xs text-slate-500">Max elevation</p>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}

            {/* Links */}
            {goal.route_url && (
              <div className="flex items-center gap-2">
                <ExternalLink className="h-4 w-4 text-slate-400" />
                <a
                  href={goal.route_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-blue-400 hover:text-blue-300"
                >
                  {goal.route_url.length > 60
                    ? goal.route_url.slice(0, 60) + "..."
                    : goal.route_url}
                </a>
              </div>
            )}

            {/* GPX status */}
            {goal.gpx_file_path && (
              <div className="flex items-center gap-2">
                <span className="inline-flex items-center gap-1.5 text-sm text-green-400">
                  <Mountain className="h-4 w-4" />
                  GPX file uploaded
                </span>
              </div>
            )}

            {/* Notes */}
            {goal.notes && (
              <div className="mt-3">
                <p className="text-xs font-medium uppercase text-slate-400">
                  Notes
                </p>
                <p className="mt-1 whitespace-pre-wrap text-sm text-slate-300">
                  {goal.notes}
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Fitness Readiness */}
        <div className="rounded-xl border border-slate-800 bg-slate-800/50 p-5">
          <h2 className="mb-4 text-lg font-semibold text-white">
            Fitness Readiness
          </h2>

          {readiness ? (
            <div className="space-y-4">
              {/* Readiness score */}
              <div className="text-center">
                <p className="text-xs font-medium uppercase text-slate-400">
                  Readiness
                </p>
                <p
                  className={`mt-1 text-3xl font-bold ${readinessColor(readiness.readiness_label)}`}
                >
                  {readiness.readiness_label}
                </p>
                <p className="mt-0.5 text-sm text-slate-500">
                  Score: {readiness.readiness_score}/100
                </p>
              </div>

              {/* Metrics */}
              <div className="grid grid-cols-2 gap-3">
                <div className="rounded-lg border border-slate-700 bg-slate-700/30 p-3">
                  <p className="text-xs text-slate-400">Current CTL</p>
                  <p className="text-lg font-bold text-white">
                    {Math.round(readiness.current_ctl)}
                  </p>
                  <p className="text-xs text-slate-500">
                    Target: {Math.round(readiness.target_ctl)}
                  </p>
                </div>
                <div className="rounded-lg border border-slate-700 bg-slate-700/30 p-3">
                  <p className="text-xs text-slate-400">Current TSB</p>
                  <p className="text-lg font-bold text-white">
                    {Math.round(readiness.current_tsb)}
                  </p>
                  {readiness.projected_tsb_on_event != null && (
                    <p className="text-xs text-slate-500">
                      Event day: ~{Math.round(readiness.projected_tsb_on_event)}
                    </p>
                  )}
                </div>
                {readiness.current_ftp && (
                  <div className="rounded-lg border border-slate-700 bg-slate-700/30 p-3">
                    <p className="text-xs text-slate-400">FTP</p>
                    <p className="text-lg font-bold text-white">
                      {readiness.current_ftp}W
                    </p>
                  </div>
                )}
                {readiness.w_per_kg && (
                  <div className="rounded-lg border border-slate-700 bg-slate-700/30 p-3">
                    <p className="text-xs text-slate-400">W/kg</p>
                    <p className="text-lg font-bold text-white">
                      {readiness.w_per_kg}
                    </p>
                  </div>
                )}
              </div>

              {/* Recommendations */}
              {readiness.recommendations.length > 0 && (
                <div>
                  <p className="text-xs font-medium uppercase text-slate-400">
                    Recommendations
                  </p>
                  <ul className="mt-2 space-y-1.5">
                    {readiness.recommendations.map((rec, i) => (
                      <li
                        key={i}
                        className="flex items-start gap-2 text-sm text-slate-300"
                      >
                        <span className="mt-0.5 h-1.5 w-1.5 shrink-0 rounded-full bg-blue-400" />
                        {rec}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ) : fitness ? (
            <div className="space-y-3">
              <div className="grid grid-cols-2 gap-3">
                <div className="rounded-lg border border-slate-700 bg-slate-700/30 p-3">
                  <p className="text-xs text-slate-400">Current Fitness</p>
                  <p className="text-lg font-bold text-white">
                    {Math.round(fitness.current_ctl)} CTL
                  </p>
                </div>
                <div className="rounded-lg border border-slate-700 bg-slate-700/30 p-3">
                  <p className="text-xs text-slate-400">Form</p>
                  <p className="text-lg font-bold text-white">
                    {Math.round(fitness.current_tsb)} TSB
                  </p>
                </div>
                {user?.ftp && (
                  <div className="rounded-lg border border-slate-700 bg-slate-700/30 p-3">
                    <p className="text-xs text-slate-400">FTP</p>
                    <p className="text-lg font-bold text-white">
                      {user.ftp}W
                    </p>
                  </div>
                )}
                {fitness.w_per_kg && (
                  <div className="rounded-lg border border-slate-700 bg-slate-700/30 p-3">
                    <p className="text-xs text-slate-400">W/kg</p>
                    <p className="text-lg font-bold text-white">
                      {fitness.w_per_kg}
                    </p>
                  </div>
                )}
              </div>
              <p className="text-xs text-slate-500">
                Detailed readiness assessment available for upcoming events.
              </p>
            </div>
          ) : (
            <p className="py-8 text-center text-sm text-slate-500">
              Upload rides with power data to see your fitness readiness.
            </p>
          )}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex flex-wrap gap-3">
        {goal.needs_assessment ? (
          <Link
            href={`/dashboard/goals/${goalId}/assess`}
            className="flex items-center gap-2 rounded-lg bg-amber-600 px-5 py-2.5 text-sm font-medium text-white hover:bg-amber-500"
          >
            <ClipboardCheck className="h-4 w-4" />
            Complete Race Report
          </Link>
        ) : goal.assessment_completed_at ? (
          <Link
            href={`/dashboard/coach?goal_id=${goalId}&debrief=true`}
            className="flex items-center gap-2 rounded-lg bg-blue-600 px-5 py-2.5 text-sm font-medium text-white hover:bg-blue-500"
          >
            <MessageCircle className="h-4 w-4" />
            Debrief with Coach Marco
          </Link>
        ) : (
          <>
            <Link
              href={`/dashboard/coach?goal_id=${goalId}`}
              className="flex items-center gap-2 rounded-lg bg-blue-600 px-5 py-2.5 text-sm font-medium text-white hover:bg-blue-500"
            >
              <MessageCircle className="h-4 w-4" />
              Ask Coach About This Goal
            </Link>
            <button
              onClick={() => generatePlan.mutate()}
              disabled={generatePlan.isPending}
              className="flex items-center gap-2 rounded-lg border border-slate-700 px-5 py-2.5 text-sm font-medium text-slate-300 hover:bg-slate-800 disabled:opacity-50"
            >
              <Zap className="h-4 w-4" />
              {generatePlan.isPending ? "Generating..." : "Generate Training Plan"}
            </button>
          </>
        )}
      </div>
    </div>
  );
}
