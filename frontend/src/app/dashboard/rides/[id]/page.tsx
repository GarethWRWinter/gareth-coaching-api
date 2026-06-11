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
  Bot,
} from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { rides, exports_, metrics, coachInsights } from "@/lib/api";
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

  const { data: debrief, isLoading: debriefLoading } = useQuery({
    queryKey: ["ride-debrief", rideId],
    queryFn: () => coachInsights.getRideDebrief(rideId),
    enabled: !!ride,
    staleTime: 1000 * 60 * 60, // 1 hour
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-vb-forest border-t-transparent" />
      </div>
    );
  }

  if (!ride) {
    return (
      <div className="py-20 text-center text-vb-text-dim">Ride not found</div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <Link
            href="/dashboard/rides"
            className="mb-2 inline-flex items-center gap-1 text-sm text-vb-text-dim hover:text-vb-forest"
          >
            <ArrowLeft className="h-4 w-4" /> Back to rides
          </Link>
          <h1 className="font-display text-3xl font-light tracking-[-0.01em] text-vb-text md:text-4xl">{ride.title}</h1>
          <p className="mt-1 text-sm text-vb-text-dim">
            {formatDate(ride.ride_date)}
            {ride.source && (
              <span className="ml-2 rounded-full bg-vb-sunken px-2 py-0.5 text-xs capitalize text-vb-text-dim">
                {ride.source.replace("_", " ")}
              </span>
            )}
            {ride.ftp_at_time && (
              <span className="ml-2 text-xs text-vb-text-muted">
                FTP: {ride.ftp_at_time}W
              </span>
            )}
          </p>
        </div>
        <button
          onClick={() => exports_.downloadGPX(rideId, ride.title)}
          className="flex items-center gap-1.5 rounded-sm border border-vb-border px-3 py-2 text-sm font-medium text-vb-forest transition-colors hover:bg-vb-surface"
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
        <StatCard label="TSS" value={ride.tss ? Math.round(ride.tss) : "-"} explainable="TSS" />
        <StatCard label="NP" value={ride.normalized_power ? Math.round(ride.normalized_power) : "-"} unit="W" explainable="Normalized Power" />
        <StatCard
          label="Avg Power"
          value={ride.average_power ? Math.round(ride.average_power) : "-"}
          unit="W"
          explainable="Average Power"
        />
        <StatCard
          label="IF"
          value={ride.intensity_factor ? ride.intensity_factor.toFixed(2) : "-"}
          explainable="Intensity Factor"
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
            <div className="flex items-center gap-1.5 rounded-full bg-vb-sage-tint px-3 py-1.5 text-sm text-vb-forest">
              <Trophy className="h-4 w-4" />
              {segments.achievement_count} achievement{segments.achievement_count !== 1 ? "s" : ""}
            </div>
          )}
          {!!segments.pr_count && (
            <div className="flex items-center gap-1.5 rounded-full border border-vb-clay/40 px-3 py-1.5 text-sm text-vb-clay">
              <Medal className="h-4 w-4" />
              {segments.pr_count} PR{segments.pr_count !== 1 ? "s" : ""}
            </div>
          )}
          {!!segments.kudos_count && (
            <div className="flex items-center gap-1.5 rounded-full bg-vb-sage-tint px-3 py-1.5 text-sm text-vb-forest">
              <ThumbsUp className="h-4 w-4" />
              {segments.kudos_count} kudo{segments.kudos_count !== 1 ? "s" : ""}
            </div>
          )}
        </div>
      )}

      {/* Coach Marco Debrief */}
      {debriefLoading && (
        <div className="flex items-center gap-3 rounded-md border border-vb-border-subtle border-l-[3px] border-l-vb-forest bg-vb-surface p-5">
          <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-vb-forest">
            <Bot className="h-5 w-5 text-white" />
          </div>
          <div className="flex items-center gap-2 text-sm text-vb-text-dim">
            <div className="h-4 w-4 animate-spin rounded-full border-2 border-vb-forest border-t-transparent" />
            Coach Marco is reviewing your ride...
          </div>
        </div>
      )}
      {debrief && (
        <div className="rounded-md border border-vb-border-subtle border-l-[3px] border-l-vb-forest bg-vb-surface p-5">
          <div className="mb-3 flex items-center gap-2">
            <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-vb-forest">
              <Bot className="h-5 w-5 text-white" />
            </div>
            <div>
              <span className="text-[11px] font-medium uppercase tracking-[0.16em] text-vb-forest">Coach Marco</span>
              <span className="ml-2 text-xs text-vb-text-muted">Post-ride debrief</span>
            </div>
          </div>
          <div className="prose prose-sm max-w-none font-light text-vb-text-dim prose-headings:font-display prose-headings:font-light prose-headings:text-vb-text prose-p:leading-relaxed prose-p:my-1.5 prose-strong:font-medium prose-strong:text-vb-text prose-em:not-italic prose-em:text-vb-clay prose-ul:my-1.5">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {debrief.debrief}
            </ReactMarkdown>
          </div>
        </div>
      )}

      {/* Ride Chart */}
      {rideData && rideData.data_points.length > 0 && (
        <div className="rounded-md border border-vb-border-subtle bg-vb-surface p-5">
          <h2 className="mb-4 font-display text-lg font-light tracking-[-0.01em] text-vb-text">
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
          <div className="rounded-md border border-vb-border-subtle bg-vb-surface p-5">
            <h2 className="mb-1 font-display text-lg font-light tracking-[-0.01em] text-vb-text">
              Power Zones
            </h2>
            <p className="mb-4 text-xs text-vb-text-muted">
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
          <div className="rounded-md border border-vb-border-subtle bg-vb-surface p-5">
            <h2 className="mb-4 font-display text-lg font-light tracking-[-0.01em] text-vb-text">
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
        <div className="rounded-md border border-vb-border-subtle bg-vb-surface p-5">
          <h2 className="mb-4 font-display text-lg font-light tracking-[-0.01em] text-vb-text">
            <Flag className="mr-2 inline h-5 w-5 text-vb-text-muted" />
            Segments ({segments.segment_efforts.length})
          </h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-vb-border-subtle text-left text-[11px] font-medium uppercase tracking-[0.14em] text-vb-text-muted">
                  <th className="pb-2 pr-4">Segment</th>
                  <th className="pb-2 pr-4">Time</th>
                  <th className="pb-2 pr-4">Avg Power</th>
                  <th className="pb-2 pr-4">Grade</th>
                  <th className="pb-2 pr-4">Category</th>
                  <th className="pb-2">Achievements</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-vb-border-subtle">
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
    <tr className="text-vb-text-dim">
      <td className="py-2.5 pr-4">
        <span className={hasPR || hasKOM ? "font-medium text-vb-text" : ""}>
          {effort.segment_name}
        </span>
        {effort.distance_meters && (
          <span className="ml-2 text-xs text-vb-text-muted">
            {(effort.distance_meters / 1000).toFixed(1)}km
          </span>
        )}
      </td>
      <td className="py-2.5 pr-4 tabular-nums">
        {formatSegmentTime(effort.elapsed_time_seconds)}
      </td>
      <td className="py-2.5 pr-4 tabular-nums">
        {effort.average_watts ? `${Math.round(effort.average_watts)}W` : "-"}
      </td>
      <td className="py-2.5 pr-4 tabular-nums">
        {effort.average_grade !== null ? `${effort.average_grade.toFixed(1)}%` : "-"}
      </td>
      <td className="py-2.5 pr-4">
        {catLabel && (
          <span className="rounded-full bg-vb-sunken px-2 py-0.5 text-xs font-medium text-vb-text-dim">
            {catLabel}
          </span>
        )}
      </td>
      <td className="py-2.5">
        <div className="flex gap-1.5">
          {hasKOM && (
            <span className="inline-flex items-center gap-1 rounded-full bg-vb-sage-tint px-2 py-0.5 text-xs font-medium text-vb-forest">
              <Crown className="h-3 w-3" />
              {effort.kom_rank === 1 ? "KOM" : `${effort.kom_rank}nd`}
            </span>
          )}
          {hasPR && (
            <span className="inline-flex items-center gap-1 rounded-full border border-vb-clay/40 px-2 py-0.5 text-xs font-medium text-vb-clay">
              <Medal className="h-3 w-3" />
              {effort.pr_rank === 1 ? "PR" : `${effort.pr_rank}${effort.pr_rank === 2 ? "nd" : effort.pr_rank === 3 ? "rd" : "th"} best`}
            </span>
          )}
        </div>
      </td>
    </tr>
  );
}
