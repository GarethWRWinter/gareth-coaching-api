"use client";

import {
  ResponsiveContainer,
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Tooltip,
} from "recharts";
import { cn } from "@/lib/utils";
import type { RiderProfileScore } from "@/lib/api";

interface RiderProfileRadarProps {
  scores: RiderProfileScore[];
  riderType: string;
  strengths: string[];
  weaknesses: string[];
  compact?: boolean;
  className?: string;
}

const RIDER_TYPE_LABELS: Record<string, { label: string; color: string }> = {
  sprinter: { label: "Sprinter", color: "text-purple-400" },
  pursuiter: { label: "Pursuiter", color: "text-orange-400" },
  time_trialist: { label: "Time Trialist", color: "text-blue-400" },
  climber: { label: "Climber", color: "text-emerald-400" },
  all_rounder: { label: "All-Rounder", color: "text-amber-400" },
  unknown: { label: "Unknown", color: "text-slate-400" },
};

function RadarTooltipContent({
  active,
  payload,
}: {
  active?: boolean;
  payload?: Array<{ payload: { label: string; score: number } }>;
}) {
  if (!active || !payload?.length) return null;
  const data = payload[0].payload;
  return (
    <div className="rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 shadow-xl">
      <p className="text-xs font-medium text-slate-300">{data.label}</p>
      <p className="text-sm font-mono font-bold text-amber-400">
        {data.score.toFixed(0)}
        <span className="ml-0.5 text-xs font-normal text-slate-500">/100</span>
      </p>
    </div>
  );
}

export function RiderProfileRadar({
  scores,
  riderType,
  strengths,
  weaknesses,
  compact = false,
  className,
}: RiderProfileRadarProps) {
  const radarData = scores.map((s) => ({
    category: s.category,
    label: s.label.replace(/ \(.*\)/, ""),
    score: s.score,
    fullMark: 100,
  }));

  const typeInfo = RIDER_TYPE_LABELS[riderType] || RIDER_TYPE_LABELS.unknown;
  const hasData = scores.some((s) => s.score > 0);

  const chartHeight = compact ? 200 : 280;
  const outerRadius = compact ? "70%" : "75%";
  const tickFontSize = compact ? 10 : 11;
  const dotRadius = compact ? 3 : 4;

  return (
    <div className={cn(compact ? "" : "rounded-xl bg-slate-900 p-4", className)}>
      {/* Header — hidden in compact mode */}
      {!compact && (
        <div className="mb-2 text-center">
          <h3 className="text-sm font-semibold text-slate-200">Rider Profile</h3>
          <span
            className={cn(
              "mt-1 inline-block rounded-full bg-slate-800 px-3 py-1 text-xs font-semibold",
              typeInfo.color
            )}
          >
            {typeInfo.label}
          </span>
        </div>
      )}

      {/* Radar Chart */}
      {hasData ? (
        <ResponsiveContainer width="100%" height={chartHeight}>
          <RadarChart data={radarData} cx="50%" cy="50%" outerRadius={outerRadius}>
            <PolarGrid stroke="#334155" strokeDasharray="3 3" />
            <PolarAngleAxis
              dataKey="label"
              tick={{ fontSize: tickFontSize, fill: "#e2e8f0" }}
            />
            <PolarRadiusAxis
              domain={[0, 100]}
              tick={{ fontSize: 9, fill: "#64748b" }}
              tickCount={compact ? 3 : 5}
              axisLine={false}
            />
            {/* Median reference area */}
            <Radar
              name="Median"
              dataKey="fullMark"
              stroke="none"
              fill="none"
            />
            {/* 50th percentile reference line */}
            <Radar
              name="Average"
              dataKey={() => 50}
              stroke="#475569"
              strokeWidth={1}
              strokeDasharray="4 4"
              fill="none"
            />
            {/* Rider's profile */}
            <Radar
              name="You"
              dataKey="score"
              stroke="#f59e0b"
              strokeWidth={2}
              fill="#f59e0b"
              fillOpacity={0.25}
              dot={{ r: dotRadius, fill: "#f59e0b", stroke: "#fbbf24" }}
            />
            <Tooltip content={<RadarTooltipContent />} />
          </RadarChart>
        </ResponsiveContainer>
      ) : (
        <div className={cn("flex items-center justify-center", compact ? "h-[200px]" : "h-[280px]")}>
          <p className="text-sm text-slate-500">
            Complete some rides with power data to see your profile
          </p>
        </div>
      )}

      {/* Strengths & Weaknesses — hidden in compact mode */}
      {!compact && (strengths.length > 0 || weaknesses.length > 0) && (
        <div className="mt-3 space-y-2">
          {strengths.length > 0 && (
            <div className="flex flex-wrap gap-1.5">
              {strengths.map((s) => (
                <span
                  key={s}
                  className="rounded-full bg-emerald-500/15 px-2.5 py-0.5 text-[11px] font-medium text-emerald-400"
                >
                  {s}
                </span>
              ))}
            </div>
          )}
          {weaknesses.length > 0 && (
            <div className="flex flex-wrap gap-1.5">
              {weaknesses.map((w) => (
                <span
                  key={w}
                  className="rounded-full bg-orange-500/15 px-2.5 py-0.5 text-[11px] font-medium text-orange-400"
                >
                  {w}
                </span>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
