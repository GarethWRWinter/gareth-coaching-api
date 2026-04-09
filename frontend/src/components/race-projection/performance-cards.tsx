"use client";

import { ArrowRight, Timer, Gauge, Zap, TrendingUp } from "lucide-react";
import type { RaceProjection } from "@/lib/api";

interface PerformanceCardsProps {
  projection: RaceProjection;
  daysUntil: number | null;
}

function formatTime(seconds: number): string {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  if (h > 0) return `${h}h ${m.toString().padStart(2, "0")}m`;
  return `${m}m`;
}

function formatTimeSaved(seconds: number): string {
  if (seconds >= 3600) {
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    return `${h}h ${m}m`;
  }
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  if (m > 0 && s > 0) return `${m}m ${s}s`;
  if (m > 0) return `${m} min`;
  return `${s}s`;
}

export function PerformanceCards({ projection, daysUntil }: PerformanceCardsProps) {
  const { current_performance, projected_performance, improvement } = projection;
  const hasProjection = projected_performance && improvement && (improvement.time_saved_seconds > 0);
  const weeksUntil = daysUntil ? Math.round(daysUntil / 7) : 0;

  return (
    <div className="space-y-3">
      <div className={`grid gap-4 ${hasProjection ? "sm:grid-cols-[1fr_auto_1fr]" : "sm:grid-cols-1 max-w-md"}`}>
        {/* Current Performance Card */}
        <div className="rounded-xl border border-slate-700 bg-slate-800/70 p-5">
          <div className="mb-3 flex items-center gap-2">
            <div className="flex h-7 w-7 items-center justify-center rounded-full bg-blue-500/15">
              <Timer className="h-3.5 w-3.5 text-blue-400" />
            </div>
            <p className="text-sm font-medium text-blue-400">
              {hasProjection ? "You Today" : "Race Day Performance"}
            </p>
          </div>

          <p className="text-3xl font-bold tracking-tight text-white">
            {formatTime(current_performance.estimated_time_seconds)}
          </p>

          <div className="mt-3 grid grid-cols-2 gap-3">
            <div className="flex items-center gap-1.5">
              <Gauge className="h-3.5 w-3.5 text-slate-500" />
              <span className="text-sm text-slate-400">
                {current_performance.avg_speed_kph} km/h
              </span>
            </div>
            <div className="flex items-center gap-1.5">
              <Zap className="h-3.5 w-3.5 text-slate-500" />
              <span className="text-sm text-slate-400">
                {current_performance.avg_power_watts}W avg
              </span>
            </div>
          </div>
        </div>

        {/* Arrow connector */}
        {hasProjection && (
          <div className="hidden items-center sm:flex">
            <div className="flex flex-col items-center gap-1">
              <ArrowRight className="h-5 w-5 text-emerald-400 animate-pulse" />
              <span className="whitespace-nowrap text-[10px] font-medium text-emerald-400/70">
                {weeksUntil}w
              </span>
            </div>
          </div>
        )}

        {/* Projected Performance Card */}
        {hasProjection && projected_performance && improvement && (
          <div className="relative rounded-xl border border-emerald-500/30 bg-slate-800/70 p-5 shadow-[0_0_20px_-5px_rgba(16,185,129,0.12)]">
            <div className="mb-3 flex items-center gap-2">
              <div className="flex h-7 w-7 items-center justify-center rounded-full bg-emerald-500/15">
                <TrendingUp className="h-3.5 w-3.5 text-emerald-400" />
              </div>
              <p className="text-sm font-medium text-emerald-400">Race Day</p>
            </div>

            <p className="text-3xl font-bold tracking-tight text-white">
              {formatTime(projected_performance.estimated_time_seconds)}
            </p>

            <div className="mt-3 grid grid-cols-2 gap-3">
              <div className="flex items-center gap-1.5">
                <Gauge className="h-3.5 w-3.5 text-slate-500" />
                <span className="text-sm text-slate-400">
                  {projected_performance.avg_speed_kph} km/h
                </span>
              </div>
              <div className="flex items-center gap-1.5">
                <Zap className="h-3.5 w-3.5 text-slate-500" />
                <span className="text-sm text-slate-400">
                  {projected_performance.avg_power_watts}W avg
                </span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Improvement callout */}
      {hasProjection && improvement && (
        <div className="flex items-center gap-2 rounded-lg bg-emerald-500/8 border border-emerald-500/15 px-4 py-2.5">
          <TrendingUp className="h-4 w-4 shrink-0 text-emerald-400" />
          <p className="text-sm text-emerald-300">
            <span className="font-semibold">{formatTimeSaved(improvement.time_saved_seconds)} faster</span>
            {improvement.ftp_gain_watts > 0 && (
              <span className="text-emerald-400/70">
                {" "}&middot; +{improvement.ftp_gain_watts}W FTP
              </span>
            )}
            {weeksUntil > 0 && (
              <span className="text-emerald-400/60">
                {" "}&mdash; {weeksUntil} weeks of focused training unlocks this
              </span>
            )}
          </p>
        </div>
      )}
    </div>
  );
}
