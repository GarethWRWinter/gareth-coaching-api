"use client";

import {
  ResponsiveContainer,
  ComposedChart,
  Area,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ReferenceLine,
} from "recharts";
import { Mountain, TrendingUp, ArrowUp, Ruler } from "lucide-react";
import { cn } from "@/lib/utils";
import type { PacingSegment } from "@/lib/api";

interface ElevationPoint {
  distance_km: number;
  elevation_m: number;
  gradient_pct?: number;
}

interface ActualDataPoint {
  distance_km: number;
  power: number | null;
  speed: number | null;
}

interface ElevationProfileChartProps {
  data: ElevationPoint[];
  pacingStrategy?: PacingSegment[];
  actualRideData?: ActualDataPoint[];
  showTargetPower?: boolean;
  showActualPower?: boolean;
  totalDistanceKm?: number;
  elevationGainM?: number;
  minElevationM?: number;
  maxElevationM?: number;
  className?: string;
}

// Zone colors matching the app's zone color scheme
const ZONE_COLORS: Record<string, string> = {
  Z1: "#94a3b8",
  Z2: "#3b82f6",
  Z3: "#22c55e",
  Z4: "#eab308",
  Z5: "#f97316",
  Z6: "#ef4444",
  Z7: "#a855f7",
};

interface MergedPoint extends ElevationPoint {
  target_power_watts?: number;
  zone?: string;
  zone_name?: string;
  estimated_speed_kph?: number;
  actual_power_watts?: number;
  actual_speed_kph?: number;
}

function mergeWithPacing(
  elevation: ElevationPoint[],
  pacing?: PacingSegment[]
): MergedPoint[] {
  if (!pacing || pacing.length === 0) {
    return elevation;
  }

  // Build a lookup from pacing by distance (nearest match)
  return elevation.map((ep) => {
    // Find the nearest pacing segment
    let closest: PacingSegment | null = null;
    let minDist = Infinity;
    for (const ps of pacing) {
      const d = Math.abs(ps.distance_km - ep.distance_km);
      if (d < minDist) {
        minDist = d;
        closest = ps;
      }
    }

    if (closest && minDist < 0.5) {
      return {
        ...ep,
        target_power_watts: closest.target_power_watts,
        zone: closest.zone,
        zone_name: closest.zone_name,
        estimated_speed_kph: closest.estimated_speed_kph,
      };
    }
    return ep;
  });
}

function mergeWithActual(
  points: MergedPoint[],
  actual?: ActualDataPoint[]
): MergedPoint[] {
  if (!actual || actual.length === 0) return points;

  // Apply rolling average to smooth power noise (5-point window)
  const smoothed = actual.map((dp, i) => {
    if (dp.power === null) return dp;
    const windowSize = 5;
    const half = Math.floor(windowSize / 2);
    const start = Math.max(0, i - half);
    const end = Math.min(actual.length, i + half + 1);
    let sum = 0;
    let count = 0;
    for (let j = start; j < end; j++) {
      if (actual[j].power !== null) {
        sum += actual[j].power!;
        count++;
      }
    }
    return { ...dp, power: count > 0 ? sum / count : dp.power };
  });

  return points.map((ep) => {
    let closest: ActualDataPoint | null = null;
    let minDist = Infinity;
    for (const ap of smoothed) {
      const d = Math.abs(ap.distance_km - ep.distance_km);
      if (d < minDist) {
        minDist = d;
        closest = ap;
      }
    }

    if (closest && minDist < 0.3) {
      return {
        ...ep,
        actual_power_watts: closest.power ?? undefined,
        actual_speed_kph: closest.speed ?? undefined,
      };
    }
    return ep;
  });
}

function ElevationTooltipContent({
  active,
  payload,
}: {
  active?: boolean;
  payload?: Array<{ payload: MergedPoint }>;
}) {
  if (!active || !payload?.length) return null;
  const data = payload[0].payload;

  return (
    <div className="rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 shadow-xl">
      <p className="mb-1 text-xs font-medium text-slate-300">
        {data.distance_km.toFixed(1)} km
      </p>
      <p className="text-sm font-mono font-medium text-emerald-400">
        {Math.round(data.elevation_m)}m
      </p>
      {data.gradient_pct !== undefined && (
        <p
          className={cn(
            "text-xs font-mono",
            data.gradient_pct > 8
              ? "text-red-400"
              : data.gradient_pct > 4
                ? "text-orange-400"
                : data.gradient_pct > 0
                  ? "text-yellow-400"
                  : "text-blue-400"
          )}
        >
          {data.gradient_pct > 0 ? "+" : ""}
          {data.gradient_pct.toFixed(1)}%
        </p>
      )}
      {(data.target_power_watts || data.actual_power_watts) && (
        <div className="mt-1.5 border-t border-slate-700 pt-1.5 space-y-0.5">
          {data.target_power_watts && data.zone && (
            <p className="text-xs text-slate-400">
              Target:{" "}
              <span
                className="font-mono font-semibold"
                style={{ color: ZONE_COLORS[data.zone] || "#94a3b8" }}
              >
                {data.target_power_watts}W
              </span>
              <span className="ml-1 text-slate-500">
                ({data.zone} {data.zone_name})
              </span>
            </p>
          )}
          {data.actual_power_watts !== undefined && (
            <p className="text-xs text-slate-400">
              Actual:{" "}
              <span className="font-mono font-semibold text-red-400">
                {Math.round(data.actual_power_watts)}W
              </span>
              {data.target_power_watts && (
                <span className={cn(
                  "ml-1 font-mono text-[10px]",
                  data.actual_power_watts > data.target_power_watts ? "text-red-400" : "text-green-400"
                )}>
                  ({data.actual_power_watts > data.target_power_watts ? "+" : ""}
                  {Math.round(data.actual_power_watts - data.target_power_watts)}W)
                </span>
              )}
            </p>
          )}
          {data.estimated_speed_kph && (
            <p className="text-xs text-slate-500">
              Target: ~{data.estimated_speed_kph} km/h
              {data.actual_speed_kph !== undefined && (
                <span className="ml-1">→ Actual: {data.actual_speed_kph.toFixed(1)} km/h</span>
              )}
            </p>
          )}
          {!data.estimated_speed_kph && data.actual_speed_kph !== undefined && (
            <p className="text-xs text-slate-500">
              {data.actual_speed_kph.toFixed(1)} km/h
            </p>
          )}
        </div>
      )}
    </div>
  );
}

export function ElevationProfileChart({
  data,
  pacingStrategy,
  actualRideData,
  showTargetPower = true,
  showActualPower = true,
  totalDistanceKm,
  elevationGainM,
  minElevationM,
  maxElevationM,
  className,
}: ElevationProfileChartProps) {
  if (!data || data.length < 2) return null;

  const hasPacing = pacingStrategy && pacingStrategy.length > 0;
  const hasActual = actualRideData && actualRideData.length > 0;
  const pacingMerged = mergeWithPacing(data, pacingStrategy);
  const mergedData = mergeWithActual(pacingMerged, actualRideData);

  // Compute stats from data if not provided
  const elevations = data.map((d) => d.elevation_m);
  const minEle = minElevationM ?? Math.min(...elevations);
  const maxEle = maxElevationM ?? Math.max(...elevations);
  const totalDist = totalDistanceKm ?? data[data.length - 1].distance_km;

  // Calculate average gradient
  const gradients = data
    .filter((d) => d.gradient_pct !== undefined)
    .map((d) => Math.abs(d.gradient_pct!));
  const avgGradient =
    gradients.length > 0
      ? gradients.reduce((a, b) => a + b, 0) / gradients.length
      : 0;

  // Y axis padding for visual appeal
  const yPad = Math.max((maxEle - minEle) * 0.1, 10);

  // Power axis domain (includes both target and actual)
  const powerValues = hasPacing
    ? pacingStrategy!.map((p) => p.target_power_watts)
    : [];
  if (hasActual) {
    for (const ap of actualRideData!) {
      if (ap.power !== null) powerValues.push(ap.power);
    }
  }
  const minPower = powerValues.length > 0 ? Math.min(...powerValues) * 0.85 : 0;
  const maxPower = powerValues.length > 0 ? Math.max(...powerValues) * 1.1 : 300;
  const showPowerAxis = hasPacing || hasActual;

  return (
    <div className={cn("space-y-4", className)}>
      {/* Summary stats */}
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        <div className="flex items-center gap-2 rounded-lg bg-slate-800/70 px-3 py-2">
          <Ruler className="h-4 w-4 text-blue-400" />
          <div>
            <p className="text-[10px] uppercase text-slate-500">Distance</p>
            <p className="text-sm font-semibold text-white">
              {totalDist.toFixed(1)} km
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2 rounded-lg bg-slate-800/70 px-3 py-2">
          <ArrowUp className="h-4 w-4 text-emerald-400" />
          <div>
            <p className="text-[10px] uppercase text-slate-500">Climbing</p>
            <p className="text-sm font-semibold text-white">
              {elevationGainM ? `${Math.round(elevationGainM)}m` : "-"}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2 rounded-lg bg-slate-800/70 px-3 py-2">
          <Mountain className="h-4 w-4 text-amber-400" />
          <div>
            <p className="text-[10px] uppercase text-slate-500">Max Elevation</p>
            <p className="text-sm font-semibold text-white">
              {Math.round(maxEle)}m
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2 rounded-lg bg-slate-800/70 px-3 py-2">
          <TrendingUp className="h-4 w-4 text-orange-400" />
          <div>
            <p className="text-[10px] uppercase text-slate-500">Avg Gradient</p>
            <p className="text-sm font-semibold text-white">
              {avgGradient.toFixed(1)}%
            </p>
          </div>
        </div>
      </div>

      {/* Chart */}
      <ResponsiveContainer width="100%" height={showPowerAxis ? 280 : 250}>
        <ComposedChart
          data={mergedData}
          margin={{ top: 10, right: showPowerAxis ? 50 : 10, left: 0, bottom: 5 }}
        >
          <defs>
            <linearGradient id="elevationGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#059669" stopOpacity={0.6} />
              <stop offset="50%" stopColor="#065f46" stopOpacity={0.4} />
              <stop offset="100%" stopColor="#064e3b" stopOpacity={0.1} />
            </linearGradient>
          </defs>
          <CartesianGrid
            strokeDasharray="3 3"
            stroke="#1e293b"
            vertical={false}
          />
          <XAxis
            dataKey="distance_km"
            type="number"
            domain={[0, "dataMax"]}
            stroke="#94a3b8"
            tick={{ fontSize: 11, fill: "#94a3b8" }}
            tickLine={{ stroke: "#475569" }}
            axisLine={{ stroke: "#475569" }}
            tickFormatter={(v: number) => `${v.toFixed(0)}km`}
          />
          <YAxis
            yAxisId="elevation"
            domain={[Math.floor(minEle - yPad), Math.ceil(maxEle + yPad)]}
            stroke="#94a3b8"
            tick={{ fontSize: 11, fill: "#94a3b8" }}
            tickLine={{ stroke: "#475569" }}
            axisLine={{ stroke: "#475569" }}
            tickFormatter={(v: number) => `${v}m`}
          />
          {showPowerAxis && (
            <YAxis
              yAxisId="power"
              orientation="right"
              domain={[Math.floor(minPower), Math.ceil(maxPower)]}
              tick={{ fontSize: 10, fill: hasPacing ? "#f59e0b" : "#ef4444" }}
              tickLine={{ stroke: "#475569" }}
              axisLine={{ stroke: "#475569" }}
              tickFormatter={(v: number) => `${v}W`}
              width={40}
            />
          )}
          <Tooltip
            content={<ElevationTooltipContent />}
            cursor={{ stroke: "#64748b", strokeDasharray: "4 4" }}
          />
          <ReferenceLine
            yAxisId="elevation"
            y={minEle}
            stroke="#475569"
            strokeDasharray="4 4"
            label={{
              value: `${Math.round(minEle)}m`,
              position: "left",
              fill: "#64748b",
              fontSize: 10,
            }}
          />
          <Area
            yAxisId="elevation"
            type="monotone"
            dataKey="elevation_m"
            stroke="#10b981"
            strokeWidth={2}
            fill="url(#elevationGradient)"
            dot={false}
            activeDot={{ r: 4, fill: "#10b981", stroke: "#059669" }}
          />
          {hasPacing && showTargetPower && (
            <Line
              yAxisId="power"
              type="monotone"
              dataKey="target_power_watts"
              stroke="#f59e0b"
              strokeWidth={1.5}
              strokeOpacity={0.7}
              dot={false}
              activeDot={{ r: 3, fill: "#f59e0b", stroke: "#0f172a", strokeWidth: 2 }}
              connectNulls
            />
          )}
          {hasActual && showActualPower && (
            <Line
              yAxisId="power"
              type="monotone"
              dataKey="actual_power_watts"
              stroke="#ef4444"
              strokeWidth={1.5}
              strokeDasharray="6 3"
              dot={false}
              activeDot={{ r: 3, fill: "#ef4444", stroke: "#0f172a", strokeWidth: 2 }}
              connectNulls
            />
          )}
          {/* Speed is shown in tooltip only — km/h values can't share the power (W) axis */}
        </ComposedChart>
      </ResponsiveContainer>

      {/* Legend */}
      {(hasPacing || hasActual) && (
        <div className="flex flex-wrap items-center gap-3 px-1">
          <div className="flex items-center gap-1.5">
            <div className="h-0.5 w-4 rounded bg-emerald-500" />
            <span className="text-[10px] text-slate-500">Elevation</span>
          </div>
          {hasPacing && showTargetPower && (
            <div className="flex items-center gap-1.5">
              <div className="h-0.5 w-4 rounded bg-amber-500" />
              <span className="text-[10px] text-slate-500">Target Power</span>
            </div>
          )}
          {hasActual && showActualPower && (
            <div className="flex items-center gap-1.5">
              <svg width="16" height="4" className="shrink-0">
                <line x1="0" y1="2" x2="16" y2="2" stroke="#ef4444" strokeWidth="2" strokeDasharray="4 2" />
              </svg>
              <span className="text-[10px] text-slate-500">Actual Power</span>
            </div>
          )}
          {hasPacing && (
            <div className="ml-auto flex items-center gap-2">
              {["Z2", "Z3", "Z4", "Z5"].map((z) => (
                <div key={z} className="flex items-center gap-1">
                  <div
                    className="h-2 w-2 rounded-full"
                    style={{ backgroundColor: ZONE_COLORS[z] }}
                  />
                  <span className="text-[10px] text-slate-500">{z}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
