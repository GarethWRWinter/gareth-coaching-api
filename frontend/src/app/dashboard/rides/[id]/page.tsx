"use client";

import { useQuery } from "@tanstack/react-query";
import { useParams } from "next/navigation";
import Link from "next/link";
import {
  ArrowLeft,
  Clock,
  Zap,
  Heart,
  Activity,
  Mountain,
  Download,
  Trophy,
  Crown,
  Medal,
  ThumbsUp,
  Flag,
} from "lucide-react";
import { rides, exports_, metrics } from "@/lib/api";
import type { SegmentEffort } from "@/lib/api";
import { formatDuration, formatDate, formatPower } from "@/lib/utils";
import { RideChart } from "@/components/charts/ride-chart";
import { PowerCurveChart } from "@/components/charts/power-curve-chart";
import { RideZonesChart } from "@/components/charts/ride-zones-chart";
import { StatCard } from "@/components/ui/stat-card";

export default function RideDetailPage() {
  const params = useParams();
  const rideId = params.id as string;

  const { data: ride, isLoading } = useQuery({
    queryKey: ["ride", rideId],
    queryFn: () => rides.get(rideId),
  });

  const { data: rideData } = useQuery({
    queryKey: ["ride-data", rideId],
    queryFn: () => rides.getData(rideId, "5s"),
    enabled: !!ride,
  });

  const { data: powerCurve } = useQuery({
    queryKey: ["ride-power-curve", rideId],
    queryFn: () => rides.getPowerCurve(rideId),
    enabled: !!ride,
  });

  const { data: rideZones } = useQuery({
    queryKey: ["ride-zones", rideId],
    queryFn: () => metrics.getRideZones(rideId),
    enabled: !!ride,
  });

  const { data: segments } = useQuery({
    queryKey: ["ride-segments", rideId],
    queryFn: () => rides.getSegments(rideId),
    enabled: !!ride,
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-blue-500 border-t-transparent" />
      </div>
    );
  }

  if (!ride) {
    return (
      <div className="py-20 text-center text-slate-400">Ride not found</div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <Link
            href="/dashboard/rides"
            className="mb-2 inline-flex items-center gap-1 text-sm text-slate-400 hover:text-white"
          >
            <ArrowLeft className="h-4 w-4" /> Back to rides
          </Link>
          <h1 className="text-2xl font-bold text-white">{ride.title}</h1>
          <p className="mt-1 text-sm text-slate-400">
            {formatDate(ride.ride_date)}
            {ride.source && (
              <span className="ml-2 rounded bg-slate-700 px-1.5 py-0.5 text-xs capitalize">
                {ride.source.replace("_", " ")}
              </span>
            )}
            {ride.ftp_at_time && (
              <span className="ml-2 text-xs text-slate-500">
                FTP: {ride.ftp_at_time}W
              </span>
            )}
          </p>
        </div>
        <button
          onClick={() => exports_.downloadGPX(rideId, ride.title)}
          className="flex items-center gap-1.5 rounded-lg border border-slate-700 px-3 py-2 text-sm text-slate-300 hover:bg-slate-800"
        >
          <Download className="h-4 w-4" /> GPX
        </button>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 gap-4 md:grid-cols-4 lg:grid-cols-6">
        <StatCard
          label="Duration"
          value={ride.duration_seconds ? formatDuration(ride.duration_seconds) : "-"}
        />
        <StatCard
          label="Distance"
          value={
            ride.distance_meters
              ? `${(ride.distance_meters / 1000).toFixed(1)}`
              : "-"
          }
          unit="km"
        />
        <StatCard label="TSS" value={ride.tss ? Math.round(ride.tss) : "-"} />
        <StatCard label="NP" value={ride.normalized_power ? Math.round(ride.normalized_power) : "-"} unit="W" />
        <StatCard
          label="Avg Power"
          value={ride.average_power ? Math.round(ride.average_power) : "-"}
          unit="W"
        />
        <StatCard
          label="IF"
          value={ride.intensity_factor ? ride.intensity_factor.toFixed(2) : "-"}
        />
        <StatCard
          label="Avg HR"
          value={ride.average_hr ?? "-"}
          unit="bpm"
        />
        <StatCard
          label="Max HR"
          value={ride.max_hr ?? "-"}
          unit="bpm"
        />
        <StatCard
          label="Avg Cadence"
          value={ride.average_cadence ?? "-"}
          unit="rpm"
        />
        <StatCard
          label="Elevation"
          value={
            ride.elevation_gain_meters
              ? Math.round(ride.elevation_gain_meters)
              : "-"
          }
          unit="m"
        />
        <StatCard
          label="Calories"
          value={ride.calories ?? "-"}
          unit="kcal"
        />
        <StatCard
          label="Max Power"
          value={ride.max_power ?? "-"}
          unit="W"
        />
      </div>

      {/* Achievements Bar */}
      {segments && (segments.achievement_count || segments.pr_count || segments.kudos_count) && (
        <div className="flex flex-wrap gap-3">
          {!!segments.achievement_count && (
            <div className="flex items-center gap-1.5 rounded-lg border border-amber-800/50 bg-amber-900/20 px-3 py-1.5 text-sm text-amber-400">
              <Trophy className="h-4 w-4" />
              {segments.achievement_count} achievement{segments.achievement_count !== 1 ? "s" : ""}
            </div>
          )}
          {!!segments.pr_count && (
            <div className="flex items-center gap-1.5 rounded-lg border border-orange-800/50 bg-orange-900/20 px-3 py-1.5 text-sm text-orange-400">
              <Medal className="h-4 w-4" />
              {segments.pr_count} PR{segments.pr_count !== 1 ? "s" : ""}
            </div>
          )}
          {!!segments.kudos_count && (
            <div className="flex items-center gap-1.5 rounded-lg border border-blue-800/50 bg-blue-900/20 px-3 py-1.5 text-sm text-blue-400">
              <ThumbsUp className="h-4 w-4" />
              {segments.kudos_count} kudo{segments.kudos_count !== 1 ? "s" : ""}
            </div>
          )}
        </div>
      )}

      {/* Ride Chart */}
      {rideData && rideData.data_points.length > 0 && (
        <div className="rounded-xl border border-slate-800 bg-slate-800/50 p-5">
          <h2 className="mb-4 text-lg font-semibold text-white">
            Ride Data
          </h2>
          <div className="h-80">
            <RideChart data={rideData.data_points} />
          </div>
        </div>
      )}

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Power Zone Distribution */}
        {rideZones && rideZones.zones.length > 0 && (
          <div className="rounded-xl border border-slate-800 bg-slate-800/50 p-5">
            <h2 className="mb-1 text-lg font-semibold text-white">
              Power Zones
            </h2>
            <p className="mb-4 text-xs text-slate-500">
              Based on FTP {rideZones.ftp}W at time of ride
            </p>
            <RideZonesChart
              zones={rideZones.zones}
              totalSeconds={rideZones.total_seconds}
            />
          </div>
        )}

        {/* Power Curve */}
        {powerCurve && powerCurve.points.length > 0 && (
          <div className="rounded-xl border border-slate-800 bg-slate-800/50 p-5">
            <h2 className="mb-4 text-lg font-semibold text-white">
              Power Curve
            </h2>
            <div className="h-64">
              <PowerCurveChart data={powerCurve.points} />
            </div>
          </div>
        )}
      </div>

      {/* Segments */}
      {segments && segments.segment_efforts.length > 0 && (
        <div className="rounded-xl border border-slate-800 bg-slate-800/50 p-5">
          <h2 className="mb-4 text-lg font-semibold text-white">
            <Flag className="mr-2 inline h-5 w-5 text-slate-400" />
            Segments ({segments.segment_efforts.length})
          </h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-700 text-left text-xs uppercase text-slate-500">
                  <th className="pb-2 pr-4">Segment</th>
                  <th className="pb-2 pr-4">Time</th>
                  <th className="pb-2 pr-4">Avg Power</th>
                  <th className="pb-2 pr-4">Grade</th>
                  <th className="pb-2 pr-4">Category</th>
                  <th className="pb-2">Achievements</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {segments.segment_efforts.map((effort) => (
                  <SegmentRow key={effort.id} effort={effort} />
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

function formatSegmentTime(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}:${s.toString().padStart(2, "0")}`;
}

function climbCategoryLabel(cat: number | null): string | null {
  if (cat === null || cat === undefined) return null;
  if (cat === 0) return null;
  if (cat === 5) return "HC";
  return `Cat ${cat}`;
}

function SegmentRow({ effort }: { effort: SegmentEffort }) {
  const hasPR = effort.pr_rank !== null && effort.pr_rank > 0;
  const hasKOM = effort.kom_rank !== null && effort.kom_rank > 0;
  const catLabel = climbCategoryLabel(effort.climb_category);

  return (
    <tr className="text-slate-300">
      <td className="py-2.5 pr-4">
        <span className={hasPR || hasKOM ? "font-semibold text-white" : ""}>
          {effort.segment_name}
        </span>
        {effort.distance_meters && (
          <span className="ml-2 text-xs text-slate-500">
            {(effort.distance_meters / 1000).toFixed(1)}km
          </span>
        )}
      </td>
      <td className="py-2.5 pr-4 font-mono tabular-nums">
        {formatSegmentTime(effort.elapsed_time_seconds)}
      </td>
      <td className="py-2.5 pr-4">
        {effort.average_watts ? `${Math.round(effort.average_watts)}W` : "-"}
      </td>
      <td className="py-2.5 pr-4">
        {effort.average_grade !== null ? `${effort.average_grade.toFixed(1)}%` : "-"}
      </td>
      <td className="py-2.5 pr-4">
        {catLabel && (
          <span className="rounded bg-slate-700 px-1.5 py-0.5 text-xs font-medium text-slate-300">
            {catLabel}
          </span>
        )}
      </td>
      <td className="py-2.5">
        <div className="flex gap-1.5">
          {hasKOM && (
            <span className="inline-flex items-center gap-1 rounded bg-yellow-900/40 px-1.5 py-0.5 text-xs font-medium text-yellow-400">
              <Crown className="h-3 w-3" />
              {effort.kom_rank === 1 ? "KOM" : `${effort.kom_rank}nd`}
            </span>
          )}
          {hasPR && (
            <span className="inline-flex items-center gap-1 rounded bg-orange-900/40 px-1.5 py-0.5 text-xs font-medium text-orange-400">
              <Medal className="h-3 w-3" />
              {effort.pr_rank === 1 ? "PR" : `${effort.pr_rank}${effort.pr_rank === 2 ? "nd" : effort.pr_rank === 3 ? "rd" : "th"} best`}
            </span>
          )}
        </div>
      </td>
    </tr>
  );
}
