"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useParams } from "next/navigation";
import Link from "next/link";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import {
  ArrowLeft,
  Download,
  Clock,
  Zap,
  ChevronDown,
  Play,
  Sparkles,
  RefreshCw,
  TrendingUp,
  Activity,
} from "lucide-react";
import { training, exports_ } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { formatDuration, cn } from "@/lib/utils";

const STEP_COLORS: Record<string, string> = {
  warmup: "bg-green-600/60",
  steady_state: "bg-blue-600/60",
  interval_on: "bg-red-600/60",
  interval_off: "bg-slate-600/60",
  cooldown: "bg-cyan-600/60",
  free_ride: "bg-purple-600/60",
  ramp: "bg-yellow-600/60",
};

const EXPORT_FORMATS = [
  { key: "zwo", label: "ZWO", desc: "Zwift" },
  { key: "erg", label: "ERG", desc: "Wahoo / TrainerRoad" },
  { key: "mrc", label: "MRC", desc: "% FTP format" },
  { key: "fit", label: "FIT", desc: "Garmin / Hammerhead" },
] as const;

export default function WorkoutDetailPage() {
  const params = useParams();
  const workoutId = params.id as string;
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const ftp = user?.ftp || 200;
  const [showExportMenu, setShowExportMenu] = useState(false);
  const [downloading, setDownloading] = useState<string | null>(null);

  const { data: workout, isLoading } = useQuery({
    queryKey: ["workout", workoutId],
    queryFn: () => training.getWorkout(workoutId),
  });

  const hasActualRide = !!workout?.actual_ride_id;

  // Auto-generate assessment the first time we view a workout with a linked ride.
  const { data: assessment, isFetching: assessmentLoading } = useQuery({
    queryKey: ["workout-assessment", workoutId],
    queryFn: () => training.getWorkoutAssessment(workoutId),
    enabled: hasActualRide,
  });

  const regenerateAssessment = useMutation({
    mutationFn: () => training.getWorkoutAssessment(workoutId, true),
    onSuccess: (data) => {
      queryClient.setQueryData(["workout-assessment", workoutId], data);
      queryClient.invalidateQueries({ queryKey: ["workout", workoutId] });
      queryClient.invalidateQueries({ queryKey: ["workouts-week"] });
    },
  });

  const handleDownload = async (format: string) => {
    if (!workout) return;
    setDownloading(format);
    setShowExportMenu(false);
    try {
      const fn =
        format === "zwo"
          ? exports_.downloadZWO
          : format === "erg"
            ? exports_.downloadERG
            : format === "mrc"
              ? exports_.downloadMRC
              : exports_.downloadFIT;
      await fn(workoutId, workout.title);
    } catch (e) {
      console.error("Download failed:", e);
    } finally {
      setDownloading(null);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-blue-500 border-t-transparent" />
      </div>
    );
  }

  if (!workout) {
    return (
      <div className="py-20 text-center text-slate-400">Workout not found</div>
    );
  }

  // Calculate total duration from steps
  const totalFromSteps =
    workout.steps?.reduce((sum, s) => {
      const repeats = s.repeat_count || 1;
      return sum + s.duration_seconds * repeats;
    }, 0) || 0;

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      {/* Header */}
      <div>
        <Link
          href="/dashboard/training"
          className="mb-2 inline-flex items-center gap-1 text-sm text-slate-400 hover:text-white"
        >
          <ArrowLeft className="h-4 w-4" /> Back to training
        </Link>
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white">{workout.title}</h1>
            <p className="mt-1 text-sm text-slate-400">
              {workout.description}
            </p>
            <div className="mt-2 flex items-center gap-4 text-sm text-slate-400">
              <span className="flex items-center gap-1">
                <Clock className="h-4 w-4" />
                {workout.planned_duration_seconds
                  ? formatDuration(workout.planned_duration_seconds)
                  : "N/A"}
              </span>
              {workout.planned_tss && (
                <span className="flex items-center gap-1">
                  <Zap className="h-4 w-4" />
                  {Math.round(workout.planned_tss)} TSS
                </span>
              )}
              <span
                className={cn(
                  "rounded-full px-2.5 py-0.5 text-xs font-medium capitalize",
                  workout.status === "completed"
                    ? "bg-green-600/20 text-green-400"
                    : workout.status === "skipped"
                      ? "bg-slate-600/20 text-slate-400"
                      : "bg-blue-600/20 text-blue-400"
                )}
              >
                {workout.status}
              </span>
            </div>
          </div>

          {/* Action buttons */}
          <div className="flex items-center gap-2">
            {/* Start Session button */}
            {workout.status === "planned" && workout.steps && workout.steps.length > 0 && (
              <Link
                href={`/dashboard/training/${workoutId}/session`}
                className="flex items-center gap-1.5 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-500 transition-colors"
              >
                <Play className="h-4 w-4" /> Start Session
              </Link>
            )}

            {/* Export dropdown */}
            {workout.steps && workout.steps.length > 0 && (
              <div className="relative">
                <button
                  onClick={() => setShowExportMenu(!showExportMenu)}
                  className="flex items-center gap-1.5 rounded-lg border border-slate-700 px-3 py-2 text-sm text-slate-300 hover:bg-slate-800 transition-colors"
                >
                  <Download className="h-4 w-4" />
                  {downloading ? "..." : "Export"}
                  <ChevronDown className="h-3 w-3" />
                </button>

                {showExportMenu && (
                  <>
                    <div
                      className="fixed inset-0 z-10"
                      onClick={() => setShowExportMenu(false)}
                    />
                    <div className="absolute right-0 top-full z-20 mt-1 w-52 rounded-lg border border-slate-700 bg-slate-800 py-1 shadow-xl">
                      {EXPORT_FORMATS.map((fmt) => (
                        <button
                          key={fmt.key}
                          onClick={() => handleDownload(fmt.key)}
                          disabled={!!downloading}
                          className="flex w-full items-center justify-between px-4 py-2 text-left text-sm hover:bg-slate-700/50 transition-colors disabled:opacity-50"
                        >
                          <span className="font-medium text-white">
                            .{fmt.label}
                          </span>
                          <span className="text-xs text-slate-400">
                            {fmt.desc}
                          </span>
                        </button>
                      ))}
                    </div>
                  </>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Planned vs Actual — shown when a ride has been linked to this workout */}
      {hasActualRide && workout.actual_ride && (
        <div className="rounded-xl border border-slate-800 bg-slate-800/50 p-5">
          <div className="mb-4 flex items-center justify-between gap-2">
            <h2 className="flex items-center gap-2 text-sm font-semibold text-white">
              <Activity className="h-4 w-4 text-blue-400" />
              Planned vs. Actual
            </h2>
            {assessment?.score != null && (
              <div
                className={cn(
                  "flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-semibold",
                  assessment.score >= 8
                    ? "bg-green-500/15 text-green-400 border border-green-500/30"
                    : assessment.score >= 6
                      ? "bg-yellow-500/15 text-yellow-400 border border-yellow-500/30"
                      : "bg-orange-500/15 text-orange-400 border border-orange-500/30"
                )}
              >
                <TrendingUp className="h-3.5 w-3.5" />
                {assessment.score.toFixed(1)}/10
              </div>
            )}
          </div>

          {/* Stat comparison grid */}
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
            <StatCompare
              label="Duration"
              planned={
                workout.planned_duration_seconds
                  ? formatDuration(workout.planned_duration_seconds)
                  : "—"
              }
              actual={
                workout.actual_ride.moving_time_seconds ||
                workout.actual_ride.duration_seconds
                  ? formatDuration(
                      (workout.actual_ride.moving_time_seconds ??
                        workout.actual_ride.duration_seconds)!
                    )
                  : "—"
              }
            />
            <StatCompare
              label="TSS"
              planned={
                workout.planned_tss != null
                  ? Math.round(workout.planned_tss).toString()
                  : "—"
              }
              actual={
                workout.actual_ride.tss != null
                  ? Math.round(workout.actual_ride.tss).toString()
                  : "—"
              }
            />
            <StatCompare
              label="IF"
              planned={
                workout.planned_if != null
                  ? workout.planned_if.toFixed(2)
                  : "—"
              }
              actual={
                workout.actual_ride.intensity_factor != null
                  ? workout.actual_ride.intensity_factor.toFixed(2)
                  : "—"
              }
            />
            <StatCompare
              label="NP"
              planned="—"
              actual={
                workout.actual_ride.normalized_power != null
                  ? `${Math.round(workout.actual_ride.normalized_power)}W`
                  : "—"
              }
            />
          </div>

          {/* Marco's feedback */}
          <div className="mt-5 rounded-lg border border-blue-500/30 bg-blue-500/5 p-4">
            <div className="mb-2 flex items-center justify-between gap-2">
              <div className="flex items-center gap-2">
                <div className="flex h-6 w-6 items-center justify-center rounded-full bg-blue-600/80">
                  <Sparkles className="h-3 w-3 text-white" />
                </div>
                <p className="text-xs font-semibold text-blue-300">
                  Coach Marco&apos;s debrief
                </p>
              </div>
              <button
                onClick={() => regenerateAssessment.mutate()}
                disabled={
                  regenerateAssessment.isPending || assessmentLoading
                }
                className="flex items-center gap-1 rounded text-[10px] text-slate-400 hover:text-blue-400 disabled:opacity-50"
                title="Regenerate feedback"
              >
                <RefreshCw
                  className={cn(
                    "h-3 w-3",
                    (regenerateAssessment.isPending || assessmentLoading) &&
                      "animate-spin"
                  )}
                />
                Regenerate
              </button>
            </div>
            {assessmentLoading && !assessment ? (
              <p className="text-xs text-slate-400">
                Marco is reviewing your ride…
              </p>
            ) : assessment?.feedback ? (
              <div className="prose prose-invert prose-sm max-w-none prose-p:text-slate-200">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {assessment.feedback}
                </ReactMarkdown>
              </div>
            ) : (
              <p className="text-xs text-slate-500">
                No feedback yet.
              </p>
            )}

            {assessment?.adjustments && assessment.adjustments.length > 0 && (
              <div className="mt-4 border-t border-blue-500/20 pt-3">
                <p className="mb-2 text-[10px] font-semibold uppercase tracking-wide text-blue-300">
                  Suggested adjustments
                </p>
                <ul className="space-y-2">
                  {assessment.adjustments.map((adj, i) => (
                    <li
                      key={i}
                      className="rounded-md border border-slate-700 bg-slate-800/60 p-2.5 text-xs text-slate-300"
                    >
                      {adj.date && (
                        <p className="mb-0.5 font-medium text-slate-200">
                          {adj.date}
                        </p>
                      )}
                      {adj.change && <p>{adj.change}</p>}
                      {adj.reason && (
                        <p className="mt-1 text-[10px] text-slate-500">
                          {adj.reason}
                        </p>
                      )}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Visual Workout Profile */}
      {workout.steps && workout.steps.length > 0 && (
        <div className="rounded-xl border border-slate-800 bg-slate-800/50 p-5">
          <h2 className="mb-4 text-sm font-semibold text-white">
            Workout Profile
          </h2>

          {/* Visual bar chart of steps */}
          <div className="flex h-32 items-end gap-0.5">
            {(() => {
              const bars: React.ReactNode[] = [];
              const steps = workout.steps || [];

              for (let si = 0; si < steps.length; si++) {
                const step = steps[si];
                const repeats = step.repeat_count || 1;
                const powerPct = step.power_target_pct || 0.5;
                const heightPct = Math.max(20, Math.min(100, powerPct * 80));
                const widthPct =
                  ((step.duration_seconds * repeats) / totalFromSteps) * 100;

                // For interval_on with repeats, interleave with the next interval_off step
                if (
                  step.step_type === "interval_on" &&
                  step.repeat_count &&
                  step.repeat_count > 1
                ) {
                  // Find the paired interval_off (next step)
                  const offStep = si + 1 < steps.length && steps[si + 1].step_type === "interval_off"
                    ? steps[si + 1]
                    : null;
                  const offPowerPct = offStep?.power_target_pct || 0.4;
                  const offHeightPct = Math.max(20, Math.min(100, offPowerPct * 80));
                  const offWidthPct = offStep
                    ? ((offStep.duration_seconds) / totalFromSteps) * 100
                    : 0;

                  for (let r = 0; r < repeats; r++) {
                    // On bar
                    bars.push(
                      <div
                        key={`${step.id}-on-${r}`}
                        className={cn(
                          "rounded-t-sm transition-all",
                          STEP_COLORS.interval_on
                        )}
                        style={{
                          height: `${heightPct}%`,
                          width: `${widthPct / repeats}%`,
                          minWidth: "2px",
                        }}
                        title={`${step.notes || "Interval"} - ${Math.round(powerPct * 100)}% FTP (${Math.round(powerPct * ftp)}W)`}
                      />
                    );
                    // Off bar (between reps, not after the last one)
                    if (offStep && r < repeats - 1) {
                      bars.push(
                        <div
                          key={`${step.id}-off-${r}`}
                          className={cn(
                            "rounded-t-sm transition-all",
                            STEP_COLORS.interval_off
                          )}
                          style={{
                            height: `${offHeightPct}%`,
                            width: `${offWidthPct}%`,
                            minWidth: "2px",
                          }}
                          title={`Recovery - ${Math.round(offPowerPct * 100)}% FTP (${Math.round(offPowerPct * ftp)}W)`}
                        />
                      );
                    }
                  }

                  // Skip the interval_off step since we already rendered it inline
                  if (offStep) si++;
                  continue;
                }

                bars.push(
                  <div
                    key={step.id}
                    className={cn(
                      "rounded-t-sm transition-all",
                      STEP_COLORS[step.step_type] || "bg-slate-600/60"
                    )}
                    style={{
                      height: `${heightPct}%`,
                      width: `${widthPct}%`,
                      minWidth: "4px",
                    }}
                    title={`${step.notes || step.step_type} - ${Math.round(powerPct * 100)}% FTP (${Math.round(powerPct * ftp)}W)`}
                  />
                );
              }
              return bars;
            })()}
          </div>

          {/* FTP line reference */}
          <div className="relative mt-1">
            <div className="absolute -top-[calc(80%+4px)] left-0 w-full border-t border-dashed border-slate-500/30" />
            <p className="text-right text-[10px] text-slate-500">
              FTP ({ftp}W)
            </p>
          </div>
        </div>
      )}

      {/* Step Details */}
      {workout.steps && workout.steps.length > 0 && (
        <div className="rounded-xl border border-slate-800 bg-slate-800/50">
          <div className="border-b border-slate-700 px-5 py-3">
            <h2 className="text-sm font-semibold text-white">Workout Steps</h2>
          </div>
          <div className="divide-y divide-slate-800">
            {workout.steps.map((step) => {
              const powerW = step.power_target_pct
                ? Math.round(step.power_target_pct * ftp)
                : null;
              const lowW = step.power_low_pct
                ? Math.round(step.power_low_pct * ftp)
                : null;
              const highW = step.power_high_pct
                ? Math.round(step.power_high_pct * ftp)
                : null;

              return (
                <div key={step.id} className="flex items-center gap-4 px-5 py-3">
                  <div
                    className={cn(
                      "h-8 w-1.5 rounded-full",
                      STEP_COLORS[step.step_type] || "bg-slate-600"
                    )}
                  />
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <p className="text-sm font-medium capitalize text-white">
                        {step.step_type.replace("_", " ")}
                      </p>
                      {step.repeat_count && step.repeat_count > 1 && (
                        <span className="rounded bg-slate-700 px-1.5 py-0.5 text-[10px] text-slate-300">
                          x{step.repeat_count}
                        </span>
                      )}
                    </div>
                    {step.notes && (
                      <p className="text-xs text-slate-400">{step.notes}</p>
                    )}
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-white">
                      {formatDuration(step.duration_seconds)}
                    </p>
                    <p className="text-xs text-slate-400">
                      {lowW && highW
                        ? `${lowW}-${highW}W`
                        : powerW
                          ? `${powerW}W`
                          : ""}
                      {step.power_target_pct &&
                        ` (${Math.round(step.power_target_pct * 100)}%)`}
                    </p>
                    {step.cadence_target && (
                      <p className="text-[10px] text-slate-500">
                        {step.cadence_target} rpm
                      </p>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}

function StatCompare({
  label,
  planned,
  actual,
}: {
  label: string;
  planned: string;
  actual: string;
}) {
  return (
    <div className="rounded-lg border border-slate-700 bg-slate-800/60 p-3">
      <p className="text-[10px] uppercase tracking-wide text-slate-500">
        {label}
      </p>
      <div className="mt-1 space-y-0.5">
        <div className="flex items-baseline justify-between gap-2">
          <span className="text-[9px] uppercase text-slate-600">Plan</span>
          <span className="text-sm font-mono text-slate-300">{planned}</span>
        </div>
        <div className="flex items-baseline justify-between gap-2">
          <span className="text-[9px] uppercase text-green-500/70">Did</span>
          <span className="text-sm font-mono text-green-400">{actual}</span>
        </div>
      </div>
    </div>
  );
}
