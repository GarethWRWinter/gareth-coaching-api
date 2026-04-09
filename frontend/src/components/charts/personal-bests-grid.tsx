"use client";

import Link from "next/link";
import { Trophy, Zap, Flame, Wind, Mountain } from "lucide-react";
import { cn } from "@/lib/utils";

interface PBPoint {
  duration_seconds: number;
  duration_label: string;
  best_power: number;
  watts_per_kg: number | null;
  ride_id: string | null;
  ride_date: string | null;
  all_time_power: number | null;
  all_time_watts_per_kg: number | null;
  all_time_ride_date: string | null;
}

interface PersonalBestsGridProps {
  points: PBPoint[];
  days?: number | null;
  className?: string;
}

function durationBand(seconds: number): {
  color: string;
  bgColor: string;
  borderColor: string;
  icon: React.ReactNode;
} {
  if (seconds <= 30) {
    return {
      color: "text-purple-400",
      bgColor: "bg-purple-500/10",
      borderColor: "border-purple-500/30",
      icon: <Zap className="h-3.5 w-3.5 text-purple-400" />,
    };
  }
  if (seconds <= 300) {
    return {
      color: "text-orange-400",
      bgColor: "bg-orange-500/10",
      borderColor: "border-orange-500/30",
      icon: <Flame className="h-3.5 w-3.5 text-orange-400" />,
    };
  }
  if (seconds <= 1800) {
    return {
      color: "text-blue-400",
      bgColor: "bg-blue-500/10",
      borderColor: "border-blue-500/30",
      icon: <Wind className="h-3.5 w-3.5 text-blue-400" />,
    };
  }
  return {
    color: "text-emerald-400",
    bgColor: "bg-emerald-500/10",
    borderColor: "border-emerald-500/30",
    icon: <Mountain className="h-3.5 w-3.5 text-emerald-400" />,
  };
}

function formatPBDate(dateStr: string): string {
  const d = new Date(dateStr);
  const now = new Date();
  const diffMs = now.getTime() - d.getTime();
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
  if (diffDays === 0) return "Today";
  if (diffDays === 1) return "Yesterday";
  if (diffDays < 30) return `${diffDays}d ago`;
  if (diffDays < 365) return `${Math.floor(diffDays / 30)}mo ago`;
  return d.toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "2-digit" });
}

export function PersonalBestsGrid({ points, days, className }: PersonalBestsGridProps) {
  const validPoints = points.filter(
    (p) => p.best_power > 0 || (p.all_time_power && p.all_time_power > 0)
  );

  if (validPoints.length === 0) return null;

  const label = days ? `Last ${days} Days` : "All Time";

  return (
    <div className={cn("rounded-xl bg-slate-900 p-4", className)}>
      <div className="mb-4 flex items-center gap-2">
        <Trophy className="h-4 w-4 text-amber-400" />
        <h3 className="text-sm font-semibold text-slate-200">Personal Bests</h3>
        {days && (
          <span className="rounded-full bg-blue-500/15 px-2 py-0.5 text-[10px] font-medium text-blue-400">
            Current Form ({label})
          </span>
        )}
      </div>

      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6">
        {validPoints.map((point) => {
          const band = durationBand(point.duration_seconds);
          const hasAllTime = point.all_time_power != null && point.all_time_power > 0;
          const isAtPB =
            hasAllTime &&
            point.best_power > 0 &&
            Math.round(point.best_power) >= Math.round(point.all_time_power!);
          const pctOfPB =
            hasAllTime && point.best_power > 0
              ? Math.round((point.best_power / point.all_time_power!) * 100)
              : null;

          const card = (
            <div
              key={point.duration_seconds}
              className={cn(
                "rounded-lg border p-3 transition-colors",
                band.borderColor,
                band.bgColor,
                point.ride_id && "hover:border-slate-500 cursor-pointer"
              )}
            >
              <div className="mb-2 flex items-center justify-between">
                <span className="text-[11px] font-medium uppercase tracking-wider text-slate-400">
                  {point.duration_label}
                </span>
                {isAtPB ? (
                  <Trophy className="h-3.5 w-3.5 text-amber-400" />
                ) : (
                  band.icon
                )}
              </div>
              {/* Current form power */}
              <div className={cn("text-xl font-bold tabular-nums", band.color)}>
                {point.best_power > 0 ? Math.round(point.best_power) : "—"}
                <span className="ml-0.5 text-xs font-normal text-slate-500">W</span>
              </div>
              {point.watts_per_kg !== null && point.best_power > 0 && (
                <div className="mt-0.5 text-xs tabular-nums text-slate-400">
                  {point.watts_per_kg.toFixed(2)} W/kg
                </div>
              )}
              {/* All-time PB comparison */}
              {hasAllTime && !isAtPB && (
                <div className="mt-1.5 border-t border-slate-700/50 pt-1.5">
                  <div className="text-[10px] text-slate-500">
                    All-time: {Math.round(point.all_time_power!)}W
                    {point.all_time_watts_per_kg != null && (
                      <span className="ml-1">
                        ({point.all_time_watts_per_kg.toFixed(1)} W/kg)
                      </span>
                    )}
                  </div>
                  {pctOfPB !== null && (
                    <div className={cn(
                      "text-[10px] font-medium",
                      pctOfPB >= 95 ? "text-green-400" :
                      pctOfPB >= 85 ? "text-yellow-400" : "text-slate-500"
                    )}>
                      {pctOfPB}% of PB
                    </div>
                  )}
                </div>
              )}
              {isAtPB && (
                <div className="mt-1.5 text-[10px] font-medium text-amber-400">
                  All-time PB!
                </div>
              )}
              {point.ride_date && (
                <div className="mt-1 text-[10px] text-slate-500">
                  {formatPBDate(point.ride_date)}
                </div>
              )}
            </div>
          );

          if (point.ride_id) {
            return (
              <Link
                key={point.duration_seconds}
                href={`/dashboard/rides/${point.ride_id}`}
              >
                {card}
              </Link>
            );
          }
          return card;
        })}
      </div>

      {/* Legend */}
      <div className="mt-3 flex flex-wrap items-center gap-4 text-[10px] text-slate-500">
        <span className="flex items-center gap-1">
          <span className="inline-block h-2 w-2 rounded-full bg-purple-500" />
          Neuromuscular
        </span>
        <span className="flex items-center gap-1">
          <span className="inline-block h-2 w-2 rounded-full bg-orange-500" />
          Anaerobic / VO2max
        </span>
        <span className="flex items-center gap-1">
          <span className="inline-block h-2 w-2 rounded-full bg-blue-500" />
          Threshold
        </span>
        <span className="flex items-center gap-1">
          <span className="inline-block h-2 w-2 rounded-full bg-emerald-500" />
          Endurance
        </span>
        {days && (
          <span className="ml-auto flex items-center gap-1">
            <Trophy className="h-2.5 w-2.5 text-amber-400" />
            = matches all-time PB
          </span>
        )}
      </div>
    </div>
  );
}
