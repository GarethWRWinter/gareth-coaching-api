"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useState, useRef, useEffect, Suspense } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import {
  Plus,
  Target,
  Calendar,
  MapPin,
  Mountain,
  ExternalLink,
  Trash2,
  Pencil,
  Upload,
  X,
  MessageCircle,
  ClipboardCheck,
  Trophy,
  Star,
} from "lucide-react";
import { goals as goalsApi, training as trainingApi } from "@/lib/api";
import { formatDate } from "@/lib/utils";
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

interface GoalFormData {
  event_name: string;
  event_date: string;
  event_type: string;
  priority: string;
  target_duration_minutes: string;
  notes: string;
  route_url: string;
}

const emptyGoalForm: GoalFormData = {
  event_name: "",
  event_date: "",
  event_type: "road_race",
  priority: "a_race",
  target_duration_minutes: "",
  notes: "",
  route_url: "",
};

function goalToFormData(goal: GoalEvent): GoalFormData {
  return {
    event_name: goal.event_name,
    event_date: goal.event_date,
    event_type: goal.event_type,
    priority: goal.priority,
    target_duration_minutes: goal.target_duration_minutes?.toString() || "",
    notes: goal.notes || "",
    route_url: goal.route_url || "",
  };
}

function formatDurationMinutes(minutes: number): string {
  const h = Math.floor(minutes / 60);
  const m = minutes % 60;
  if (h > 0) return m > 0 ? `${h}h ${m}m` : `${h}h`;
  return `${m}m`;
}

function priorityColor(priority: string): string {
  // ALMANAC: A-race gets a sage-tint forest chip. B and C get neutral
  // outlined tags.
  switch (priority) {
    case "a_race":
      return "border-transparent bg-vb-sage-tint text-vb-forest";
    default:
      return "border-vb-border text-vb-text-dim";
  }
}

function daysUntilColor(days: number): string {
  // Imminent (<=30) reads in forest; neutral after that.
  if (days <= 30) return "border-vb-forest text-vb-forest";
  return "border-vb-border text-vb-text-dim";
}

function GoalsPageInner() {
  const queryClient = useQueryClient();
  const gpxInputRef = useRef<HTMLInputElement>(null);
  const searchParams = useSearchParams();

  const [showForm, setShowForm] = useState(false);
  const [editingGoalId, setEditingGoalId] = useState<string | null>(null);
  const [goalForm, setGoalForm] = useState<GoalFormData>(emptyGoalForm);
  const [gpxUploadingId, setGpxUploadingId] = useState<string | null>(null);
  const [pendingGpxFile, setPendingGpxFile] = useState<File | null>(null);
  const [planGenerating, setPlanGenerating] = useState(false);
  const formGpxInputRef = useRef<HTMLInputElement>(null);

  // Auto-open the add-goal form when navigated with ?new=1 (e.g. from the
  // post-assessment "What's next?" prompt).
  useEffect(() => {
    if (searchParams.get("new") === "1") {
      setEditingGoalId(null);
      setGoalForm(emptyGoalForm);
      setShowForm(true);
    }
  }, [searchParams]);

  const { data: goalsData, isLoading } = useQuery({
    queryKey: ["goals"],
    queryFn: () => goalsApi.list(),
  });

  const saveGoal = useMutation({
    mutationFn: () => {
      const data: Record<string, unknown> = {
        event_name: goalForm.event_name,
        event_date: goalForm.event_date,
        event_type: goalForm.event_type,
        priority: goalForm.priority,
      };
      if (goalForm.target_duration_minutes) {
        data.target_duration_minutes = parseInt(goalForm.target_duration_minutes);
      }
      if (goalForm.notes) data.notes = goalForm.notes;
      if (goalForm.route_url) data.route_url = goalForm.route_url;

      if (editingGoalId) {
        return goalsApi.update(editingGoalId, data as Parameters<typeof goalsApi.update>[1]);
      }
      return goalsApi.create(data as Parameters<typeof goalsApi.create>[0]);
    },
    onSuccess: async (goal) => {
      // Upload pending GPX file if one was selected
      if (pendingGpxFile && goal?.id) {
        await goalsApi.uploadGpx(goal.id, pendingGpxFile);
        setPendingGpxFile(null);
      }

      // Auto-regenerate a unified training plan that considers ALL goals.
      // The backend auto-detects the primary (highest-priority A-race),
      // builds the macro periodization toward it, and accommodates B/C races.
      if (!editingGoalId && goal?.id) {
        try {
          setPlanGenerating(true);
          await trainingApi.generatePlan({
            periodization_model: "traditional",
          });
          queryClient.invalidateQueries({ queryKey: ["plans"] });
          queryClient.invalidateQueries({ queryKey: ["workouts-week"] });
        } catch (planErr) {
          console.error("Auto plan generation failed:", planErr);
        } finally {
          setPlanGenerating(false);
        }
      }

      queryClient.invalidateQueries({ queryKey: ["goals"] });
      setShowForm(false);
      setEditingGoalId(null);
      setGoalForm(emptyGoalForm);
    },
  });

  const deleteGoal = useMutation({
    mutationFn: (id: string) => goalsApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["goals"] });
    },
  });

  const uploadGpx = useMutation({
    mutationFn: ({ goalId, file }: { goalId: string; file: File }) =>
      goalsApi.uploadGpx(goalId, file),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["goals"] });
      setGpxUploadingId(null);
    },
    onError: () => {
      setGpxUploadingId(null);
    },
  });

  // Three-category split
  const upcomingGoals =
    goalsData?.goals.filter((g) => g.days_until != null && g.days_until >= 0) || [];
  const needsAssessmentGoals =
    goalsData?.goals.filter((g) => g.needs_assessment) || [];
  const completedGoals =
    goalsData?.goals.filter(
      (g) => (g.days_until == null || g.days_until < 0) && !g.needs_assessment
    ) || [];

  const inputClasses =
    "w-full rounded-sm border border-vb-border-subtle bg-vb-bg px-3 py-2 text-sm text-vb-text focus:border-vb-forest focus:outline-none";

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="h-8 w-8 animate-spin rounded-full border border-vb-border-subtle border-t-vb-forest" />
      </div>
    );
  }

  return (
    <div className="space-y-10">
      {/* ============ MASTHEAD ============ */}
      <header className="flex items-end justify-between gap-6 border-b border-vb-border-subtle pb-5">
        <div>
          <p className="mb-2 text-[11px] font-medium uppercase tracking-[0.16em] text-vb-forest">
            Calendar
          </p>
          <h1 className="font-display text-5xl font-light leading-[0.95] tracking-[-0.01em] md:text-6xl">
            Goals.
          </h1>
          <p className="mt-3 max-w-md text-sm text-vb-text-dim">
            Your target events and races. Add route data and Marco tailors
            coaching to each goal.
          </p>
        </div>
        <button
          onClick={() => {
            setEditingGoalId(null);
            setGoalForm(emptyGoalForm);
            setShowForm(true);
          }}
          className="flex shrink-0 items-center gap-2 rounded-sm bg-vb-forest px-5 py-3 text-[12px] font-medium uppercase tracking-[0.08em] text-white transition-colors hover:bg-vb-forest-soft"
        >
          <Plus className="h-3.5 w-3.5" /> Add Goal
        </button>
      </header>

      {/* Goal Form */}
      {showForm && (
        <div className="rounded-md border border-vb-border-subtle bg-vb-surface p-6">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="font-display text-2xl font-light tracking-[-0.01em] text-vb-text">
              {editingGoalId ? "Edit Goal" : "New Goal"}
            </h2>
            <button
              onClick={() => {
                setShowForm(false);
                setEditingGoalId(null);
              }}
              className="rounded-sm p-1 text-vb-text-muted hover:text-vb-text"
            >
              <X className="h-5 w-5" />
            </button>
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <label className="mb-2 block text-[11px] font-medium uppercase tracking-[0.16em] text-vb-text-muted">
                Event Name *
              </label>
              <input
                value={goalForm.event_name}
                onChange={(e) =>
                  setGoalForm({ ...goalForm, event_name: e.target.value })
                }
                placeholder="e.g. Mallorca 312, Tour of Wessex"
                className={inputClasses}
              />
            </div>
            <div>
              <label className="mb-2 block text-[11px] font-medium uppercase tracking-[0.16em] text-vb-text-muted">
                Event Date *
              </label>
              <input
                type="date"
                value={goalForm.event_date}
                onChange={(e) =>
                  setGoalForm({ ...goalForm, event_date: e.target.value })
                }
                className={inputClasses}
              />
            </div>
            <div>
              <label className="mb-2 block text-[11px] font-medium uppercase tracking-[0.16em] text-vb-text-muted">
                Event Type
              </label>
              <select
                value={goalForm.event_type}
                onChange={(e) =>
                  setGoalForm({ ...goalForm, event_type: e.target.value })
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
              <label className="mb-2 block text-[11px] font-medium uppercase tracking-[0.16em] text-vb-text-muted">
                Priority
              </label>
              <select
                value={goalForm.priority}
                onChange={(e) =>
                  setGoalForm({ ...goalForm, priority: e.target.value })
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
              <label className="mb-2 block text-[11px] font-medium uppercase tracking-[0.16em] text-vb-text-muted">
                Target Duration (minutes)
              </label>
              <input
                type="number"
                value={goalForm.target_duration_minutes}
                onChange={(e) =>
                  setGoalForm({
                    ...goalForm,
                    target_duration_minutes: e.target.value,
                  })
                }
                placeholder="e.g. 240 (4 hours)"
                className={inputClasses}
              />
            </div>
            <div>
              <label className="mb-2 block text-[11px] font-medium uppercase tracking-[0.16em] text-vb-text-muted">
                Route / Event URL
              </label>
              <input
                type="url"
                value={goalForm.route_url}
                onChange={(e) =>
                  setGoalForm({ ...goalForm, route_url: e.target.value })
                }
                placeholder="https://strava.com/routes/... or event website"
                className={inputClasses}
              />
            </div>
          </div>

          <div className="mt-4">
            <label className="mb-2 block text-[11px] font-medium uppercase tracking-[0.16em] text-vb-text-muted">
              Notes
            </label>
            <textarea
              value={goalForm.notes}
              onChange={(e) =>
                setGoalForm({ ...goalForm, notes: e.target.value })
              }
              placeholder="Course details, specific targets, strategy notes..."
              rows={3}
              className={`${inputClasses} resize-none`}
            />
          </div>

          {/* GPX Upload */}
          <div className="mt-4">
            <label className="mb-2 block text-[11px] font-medium uppercase tracking-[0.16em] text-vb-text-muted">
              GPX Route File (optional)
            </label>
            <input
              ref={formGpxInputRef}
              type="file"
              accept=".gpx"
              className="hidden"
              onChange={(e) => {
                const file = e.target.files?.[0];
                if (file) {
                  if (editingGoalId) {
                    // Editing — upload immediately
                    uploadGpx.mutate({ goalId: editingGoalId, file });
                  } else {
                    // Creating — store for upload after save
                    setPendingGpxFile(file);
                  }
                }
                e.target.value = "";
              }}
            />
            <div className="flex items-center gap-3">
              <button
                type="button"
                onClick={() => formGpxInputRef.current?.click()}
                className="flex items-center gap-1.5 rounded-sm border border-dashed border-vb-border px-3 py-2 text-sm text-vb-text-dim hover:border-vb-forest hover:text-vb-forest"
              >
                <Upload className="h-4 w-4" />
                {pendingGpxFile
                  ? "Change file"
                  : editingGoalId
                    ? "Upload / Replace GPX"
                    : "Upload GPX"}
              </button>
              {pendingGpxFile && (
                <div className="flex items-center gap-2">
                  <span className="flex items-center gap-1 text-xs text-vb-forest">
                    <Mountain className="h-3 w-3" />
                    {pendingGpxFile.name}
                  </span>
                  <button
                    type="button"
                    onClick={() => setPendingGpxFile(null)}
                    className="rounded-sm p-0.5 text-vb-text-muted hover:text-vb-clay"
                  >
                    <X className="h-3.5 w-3.5" />
                  </button>
                </div>
              )}
              {editingGoalId && !pendingGpxFile && (() => {
                const editGoal = goalsData?.goals.find((g) => g.id === editingGoalId);
                if (editGoal?.gpx_file_path) {
                  return (
                    <span className="flex items-center gap-1 text-xs text-vb-forest">
                      <Mountain className="h-3 w-3" />
                      GPX uploaded
                    </span>
                  );
                }
                return null;
              })()}
            </div>
            <p className="mt-1 text-[10px] text-vb-text-muted">
              Export from Strava, RideWithGPS, or Komoot for elevation profile and pacing analysis
            </p>
          </div>

          {!editingGoalId && (
            <p className="mt-3 text-xs text-vb-text-muted">
              After you create this goal we&apos;ll automatically build a training plan
              that peaks on race day.
            </p>
          )}

          <div className="mt-4 flex flex-wrap gap-2">
            <button
              onClick={() => saveGoal.mutate()}
              disabled={
                !goalForm.event_name ||
                !goalForm.event_date ||
                saveGoal.isPending ||
                planGenerating
              }
              className="rounded-sm bg-vb-forest px-4 py-2 text-sm font-medium text-white hover:bg-vb-forest-soft disabled:opacity-50"
            >
              {saveGoal.isPending
                ? "Saving..."
                : planGenerating
                  ? "Generating plan..."
                  : editingGoalId
                    ? "Update Goal"
                    : "Create Goal"}
            </button>
            <button
              onClick={() => {
                setShowForm(false);
                setEditingGoalId(null);
              }}
              className="rounded-sm border border-vb-border px-4 py-2 text-sm text-vb-forest hover:bg-vb-surface"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* Hidden GPX file input */}
      <input
        ref={gpxInputRef}
        type="file"
        accept=".gpx"
        className="hidden"
        onChange={(e) => {
          const file = e.target.files?.[0];
          if (file && gpxUploadingId) {
            uploadGpx.mutate({ goalId: gpxUploadingId, file });
          }
          e.target.value = "";
        }}
      />

      {/* Empty state */}
      {goalsData?.goals.length === 0 && !showForm && (
        <div className="rounded-md border border-vb-border-subtle px-6 py-16 text-center">
          <p className="mb-3 text-[11px] font-medium uppercase tracking-[0.16em] text-vb-forest">
            Empty calendar
          </p>
          <h3 className="font-display text-4xl font-light leading-tight tracking-[-0.01em]">
            What are we aiming at?
          </h3>
          <p className="mx-auto mt-4 max-w-md text-sm text-vb-text-dim">
            A sportive, a road race, a number you&apos;ve been chasing, give
            Marco the target and he&apos;ll build the season backwards from it.
            Add the route&apos;s GPX and he&apos;ll study every climb.
          </p>
          <button
            onClick={() => {
              setEditingGoalId(null);
              setGoalForm(emptyGoalForm);
              setShowForm(true);
            }}
            className="mt-8 inline-flex items-center gap-2 rounded-sm bg-vb-forest px-5 py-3 text-[12px] font-medium uppercase tracking-[0.08em] text-white transition-colors hover:bg-vb-forest-soft"
          >
            <Plus className="h-3.5 w-3.5" /> Add your first goal
          </button>
        </div>
      )}

      {/* Upcoming Goals */}
      {upcomingGoals.length > 0 && (
        <div>
          <h2 className="mb-4 text-[11px] font-medium uppercase tracking-[0.16em] text-vb-text-muted">
            Upcoming ({upcomingGoals.length})
          </h2>
          <div className="space-y-3">
            {upcomingGoals.map((goal) => (
              <GoalCard
                key={goal.id}
                goal={goal}
                onEdit={() => {
                  setEditingGoalId(goal.id);
                  setGoalForm(goalToFormData(goal));
                  setShowForm(true);
                }}
                onDelete={() => {
                  if (confirm(`Delete "${goal.event_name}"?`)) {
                    deleteGoal.mutate(goal.id);
                  }
                }}
                onUploadGpx={() => {
                  setGpxUploadingId(goal.id);
                  gpxInputRef.current?.click();
                }}
                gpxUploading={uploadGpx.isPending && gpxUploadingId === goal.id}
              />
            ))}
          </div>
        </div>
      )}

      {/* Needs Assessment */}
      {needsAssessmentGoals.length > 0 && (
        <div>
          <h2 className="mb-3 text-[11px] font-medium uppercase tracking-[0.16em] text-vb-clay">
            Needs Assessment ({needsAssessmentGoals.length})
          </h2>
          <div className="space-y-3">
            {needsAssessmentGoals.map((goal) => (
              <div key={goal.id} className="relative">
                <GoalCard
                  goal={goal}
                  onEdit={() => {
                    setEditingGoalId(goal.id);
                    setGoalForm(goalToFormData(goal));
                    setShowForm(true);
                  }}
                  onDelete={() => {
                    if (confirm(`Delete "${goal.event_name}"?`)) {
                      deleteGoal.mutate(goal.id);
                    }
                  }}
                  onUploadGpx={() => {
                    setGpxUploadingId(goal.id);
                    gpxInputRef.current?.click();
                  }}
                  gpxUploading={uploadGpx.isPending && gpxUploadingId === goal.id}
                  assessmentBanner
                />
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Completed Goals */}
      {completedGoals.length > 0 && (
        <div>
          <h2 className="mb-4 text-[11px] font-medium uppercase tracking-[0.16em] text-vb-text-muted">
            Completed ({completedGoals.length})
          </h2>
          <div className="space-y-3">
            {completedGoals.map((goal) => (
              <GoalCard
                key={goal.id}
                goal={goal}
                onEdit={() => {
                  setEditingGoalId(goal.id);
                  setGoalForm(goalToFormData(goal));
                  setShowForm(true);
                }}
                onDelete={() => {
                  if (confirm(`Delete "${goal.event_name}"?`)) {
                    deleteGoal.mutate(goal.id);
                  }
                }}
                onUploadGpx={() => {
                  setGpxUploadingId(goal.id);
                  gpxInputRef.current?.click();
                }}
                gpxUploading={uploadGpx.isPending && gpxUploadingId === goal.id}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default function GoalsPage() {
  return (
    <Suspense
      fallback={
        <div className="flex items-center justify-center py-20">
          <div className="h-8 w-8 animate-spin rounded-full border border-vb-border-subtle border-t-vb-forest" />
        </div>
      }
    >
      <GoalsPageInner />
    </Suspense>
  );
}

function GoalCard({
  goal,
  onEdit,
  onDelete,
  onUploadGpx,
  gpxUploading,
  assessmentBanner,
}: {
  goal: GoalEvent;
  onEdit: () => void;
  onDelete: () => void;
  onUploadGpx: () => void;
  gpxUploading: boolean;
  assessmentBanner?: boolean;
}) {
  return (
    <div className={`rounded-md border p-5 transition-colors ${
      assessmentBanner
        ? "border-vb-border-subtle border-l-[3px] border-l-vb-clay bg-vb-surface hover:bg-vb-surface-raised"
        : "border-vb-border-subtle bg-vb-surface hover:bg-vb-surface-raised"
    }`}>
      <div className="flex items-start justify-between">
        <div className="min-w-0 flex-1">
          {/* Title row */}
          <div className="flex items-center gap-2">
            <Link
              href={`/dashboard/goals/${goal.id}`}
              className="font-display text-lg font-light tracking-[-0.01em] text-vb-text hover:text-vb-forest"
            >
              {goal.event_name}
            </Link>
            {goal.days_until != null && goal.days_until >= 0 && (
              <span
                className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${daysUntilColor(goal.days_until)}`}
              >
                {goal.days_until === 0
                  ? "Today!"
                  : `${goal.days_until} days`}
              </span>
            )}
          </div>

          {/* Meta row */}
          <div className="mt-1.5 flex flex-wrap items-center gap-2">
            <span className="inline-flex items-center gap-1 text-xs text-vb-text-dim">
              <Calendar className="h-3 w-3" />
              {formatDate(goal.event_date)}
            </span>
            <span className="inline-flex items-center rounded-full border border-vb-border px-2 py-0.5 text-xs capitalize text-vb-text-dim">
              {goal.event_type.replace(/_/g, " ")}
            </span>
            <span
              className={`inline-flex items-center rounded-full border px-2 py-0.5 text-xs capitalize ${priorityColor(goal.priority)}`}
            >
              {goal.priority.replace(/_/g, " ")}
            </span>
            {goal.target_duration_minutes && (
              <span className="text-xs text-vb-text-dim">
                Target: {formatDurationMinutes(goal.target_duration_minutes)}
              </span>
            )}
          </div>

          {/* Route data */}
          {goal.route_data && !goal.route_data.error && (
            <div className="mt-2 flex items-center gap-3 text-xs text-vb-forest">
              <MapPin className="h-3.5 w-3.5 shrink-0" />
              {goal.route_data.total_distance_km && (
                <span>{goal.route_data.total_distance_km}km</span>
              )}
              {goal.route_data.elevation_gain_m && (
                <span className="flex items-center gap-0.5">
                  <Mountain className="h-3 w-3" />
                  {goal.route_data.elevation_gain_m}m
                </span>
              )}
              {(goal.route_data.title || goal.route_data.name) && (
                <span className="truncate text-vb-text-dim">
                  {goal.route_data.title || goal.route_data.name}
                </span>
              )}
            </div>
          )}

          {/* Notes */}
          {goal.notes && (
            <p className="mt-2 text-xs text-vb-text-muted line-clamp-2">
              {goal.notes}
            </p>
          )}

          {/* Assessment CTA or result inline */}
          {assessmentBanner && (
            <Link
              href={`/dashboard/goals/${goal.id}/assess`}
              className="mt-2 inline-flex items-center gap-1.5 rounded-sm border border-vb-clay px-3 py-1.5 text-xs font-medium text-vb-clay hover:bg-vb-clay/5"
            >
              <ClipboardCheck className="h-3.5 w-3.5" />
              Complete Race Report
            </Link>
          )}
          {goal.assessment_completed_at && (
            <div className="mt-2 flex items-center gap-3 text-xs">
              <span className={`rounded-full px-2 py-0.5 font-medium ${
                goal.status === "completed"
                  ? "bg-vb-sage-tint text-vb-forest"
                  : goal.status === "dnf"
                    ? "bg-vb-clay/15 text-vb-clay"
                    : "bg-vb-clay/15 text-vb-clay"
              }`}>
                {goal.status === "dns" ? "DNS" : goal.status === "dnf" ? "DNF" : "Completed"}
              </span>
              {goal.finish_time_seconds && (
                <span className="tabular-nums text-vb-text-dim">
                  {Math.floor(goal.finish_time_seconds / 3600)}h{" "}
                  {Math.floor((goal.finish_time_seconds % 3600) / 60)}m
                </span>
              )}
              {goal.overall_satisfaction && (
                <span className="flex items-center gap-0.5 text-vb-forest">
                  <Star className="h-3 w-3" />
                  {goal.overall_satisfaction}/10
                </span>
              )}
            </div>
          )}

          {/* Tags / indicators */}
          <div className="mt-2 flex items-center gap-2">
            {goal.route_url && (
              <a
                href={goal.route_url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1 text-xs text-vb-text-muted hover:text-vb-forest"
              >
                <ExternalLink className="h-3 w-3" />
                Event link
              </a>
            )}
            {goal.gpx_file_path && (
              <span className="inline-flex items-center gap-1 text-xs text-vb-forest">
                <Mountain className="h-3 w-3" />
                GPX
              </span>
            )}
          </div>
        </div>

        {/* Actions */}
        <div className="ml-4 flex shrink-0 flex-col gap-1">
          <Link
            href={`/dashboard/goals/${goal.id}`}
            className="rounded-sm p-1.5 text-vb-text-muted hover:bg-vb-sunken hover:text-vb-forest"
            title="View details"
          >
            <Target className="h-4 w-4" />
          </Link>
          <button
            onClick={onUploadGpx}
            disabled={gpxUploading}
            className="rounded-sm p-1.5 text-vb-text-muted hover:bg-vb-sunken hover:text-vb-forest"
            title="Upload GPX"
          >
            <Upload className="h-4 w-4" />
          </button>
          <button
            onClick={onEdit}
            className="rounded-sm p-1.5 text-vb-text-muted hover:bg-vb-sunken hover:text-vb-text"
            title="Edit"
          >
            <Pencil className="h-4 w-4" />
          </button>
          <button
            onClick={onDelete}
            className="rounded-sm p-1.5 text-vb-text-muted hover:bg-vb-sunken hover:text-vb-clay"
            title="Delete"
          >
            <Trash2 className="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
