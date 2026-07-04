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
  Z1: "#8AA3B0",
  Z2: "#9FB295",
  Z3: "#C7A458",
  Z4: "#D2855B",
  Z5: "#C06A48",
  Z6: "#A24E36",
  Z7: "#7E3A28",
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
    <div className="rounded-md border border-vb-border-subtle bg-vb-surface px-3 py-2 shadow-[0_2px_8px_rgba(33,30,26,0.10)]">
      <p className="mb-1 text-xs font-medium text-vb-text-dim">
        {data.distance_km.toFixed(1)} km
      </p>
      <p className="text-sm font-mono font-medium text-vb-forest">
        {Math.round(data.elevation_m)}m
      </p>
      {data.gradient_pct !== undefined && (
        <p
          className={cn(
            "text-xs font-mono",
            data.gradient_pct > 8
              ? "text-vb-clay"
              : data.gradient_pct > 4
                ? "text-[#D2855B]"
                : data.gradient_pct > 0
                  ? "text-vb-ochre"
                  : "text-vb-dusty"
          )}
        >
          {data.gradient_pct > 0 ? "+" : ""}
          {data.gradient_pct.toFixed(1)}%
        </p>
      )}
      {(data.target_power_watts || data.actual_power_watts) && (
        <div className="mt-1.5 border-t border-vb-border-subtle pt-1.5 space-y-0.5">
          {data.target_power_watts && data.zone && (
            <p className="text-xs text-vb-text-dim">
              Target:{" "}
              <span
                className="font-mono font-semibold"
                style={{ color: ZONE_COLORS[data.zone] || "#8AA3B0" }}
              >
                {data.target_power_watts}W
              </span>
              <span className="ml-1 text-vb-text-muted">
                ({data.zone} {data.zone_name})
              </span>
            </p>
          )}
          {data.actual_power_watts !== undefined && (
            <p className="text-xs text-vb-text-dim">
              Actual:{" "}
              <span className="font-mono font-semibold text-vb-clay">
                {Math.round(data.actual_power_watts)}W
              </span>
              {data.target_power_watts && (
                <span className={cn(
                  "ml-1 font-mono text-[10px]",
                  data.actual_power_watts > data.target_power_watts ? "text-vb-clay" : "text-vb-success"
                )}>
                  ({data.actual_power_watts > data.target_power_watts ? "+" : ""}
                  {Math.round(data.actual_power_watts - data.target_power_watts)}W)
                </span>
              )}
            </p>
          )}
          {data.estimated_speed_kph && (
            <p className="text-xs text-vb-text-muted">
              Target: ~{data.estimated_speed_kph} km/h
              {data.actual_speed_kph !== undefined && (
                <span className="ml-1">→ Actual: {data.actual_speed_kph.toFixed(1)} km/h</span>
              )}
            </p>
          )}
          {!data.estimated_speed_kph && data.actual_speed_kph !== undefined && (
            <p className="text-xs text-vb-text-muted">
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
        <div className="flex items-center gap-2 rounded-md border border-vb-border-subtle bg-vb-surface px-3 py-2">
          <Ruler className="h-4 w-4 text-vb-forest" />
          <div>
            <p className="text-[10px] uppercase text-vb-text-muted">Distance</p>
            <p className="text-sm font-semibold text-vb-text">
              {totalDist.toFixed(1)} km
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2 rounded-md border border-vb-border-subtle bg-vb-surface px-3 py-2">
          <ArrowUp className="h-4 w-4 text-vb-forest" />
          <div>
            <p className="text-[10px] uppercase text-vb-text-muted">Climbing</p>
            <p className="text-sm font-semibold text-vb-text">
              {elevationGainM ? `${Math.round(elevationGainM)}m` : "-"}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2 rounded-md border border-vb-border-subtle bg-vb-surface px-3 py-2">
          <Mountain className="h-4 w-4 text-vb-clay" />
          <div>
            <p className="text-[10px] uppercase text-vb-text-muted">Max Elevation</p>
            <p className="text-sm font-semibold text-vb-text">
              {Math.round(maxEle)}m
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2 rounded-md border border-vb-border-subtle bg-vb-surface px-3 py-2">
          <TrendingUp className="h-4 w-4 text-vb-clay" />
          <div>
            <p className="text-[10px] uppercase text-vb-text-muted">Avg Gradient</p>
            <p className="text-sm font-semibold text-vb-text">
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
              <stop offset="0%" stopColor="#36513F" stopOpacity={0.6} />
              <stop offset="50%" stopColor="#36513F" stopOpacity={0.4} />
              <stop offset="100%" stopColor="#36513F" stopOpacity={0.1} />
            </linearGradient>
          </defs>
          <CartesianGrid
            strokeDasharray="3 3"
            stroke="#E4DCCE"
            vertical={false}
          />
          <XAxis
            dataKey="distance_km"
            type="number"
            domain={[0, "dataMax"]}
            stroke="#D6CFC1"
            tick={{ fontSize: 11, fill: "#948D80" }}
            tickLine={{ stroke: "#D6CFC1" }}
            axisLine={{ stroke: "#D6CFC1" }}
            tickFormatter={(v: number) => `${v.toFixed(0)}km`}
          />
          <YAxis
            yAxisId="elevation"
            domain={[Math.floor(minEle - yPad), Math.ceil(maxEle + yPad)]}
            stroke="#D6CFC1"
            tick={{ fontSize: 11, fill: "#948D80" }}
            tickLine={{ stroke: "#D6CFC1" }}
            axisLine={{ stroke: "#D6CFC1" }}
            tickFormatter={(v: number) => `${v}m`}
          />
          {showPowerAxis && (
            <YAxis
              yAxisId="power"
              orientation="right"
              domain={[Math.floor(minPower), Math.ceil(maxPower)]}
              tick={{ fontSize: 10, fill: hasPacing ? "#C7A458" : "#BB6647" }}
              tickLine={{ stroke: "#D6CFC1" }}
              axisLine={{ stroke: "#D6CFC1" }}
              tickFormatter={(v: number) => `${v}W`}
              width={40}
            />
          )}
          <Tooltip
            content={<ElevationTooltipContent />}
            cursor={{ stroke: "#BCB3A3", strokeDasharray: "4 4" }}
          />
          <ReferenceLine
            yAxisId="elevation"
            y={minEle}
            stroke="#D6CFC1"
            strokeDasharray="4 4"
            label={{
              value: `${Math.round(minEle)}m`,
              position: "left",
              fill: "#948D80",
              fontSize: 10,
            }}
          />
          <Area
            yAxisId="elevation"
            type="monotone"
            dataKey="elevation_m"
            stroke="#36513F"
            strokeWidth={2}
            fill="url(#elevationGradient)"
            dot={false}
            activeDot={{ r: 4, fill: "#36513F", stroke: "#FBF7F0" }}
          />
          {hasPacing && showTargetPower && (
            <Line
              yAxisId="power"
              type="monotone"
              dataKey="target_power_watts"
              stroke="#C7A458"
              strokeWidth={1.5}
              strokeOpacity={0.7}
              dot={false}
              activeDot={{ r: 3, fill: "#C7A458", stroke: "#FBF7F0", strokeWidth: 2 }}
              connectNulls
            />
          )}
          {hasActual && showActualPower && (
            <Line
              yAxisId="power"
              type="monotone"
              dataKey="actual_power_watts"
              stroke="#BB6647"
              strokeWidth={1.5}
              strokeDasharray="6 3"
              dot={false}
              activeDot={{ r: 3, fill: "#BB6647", stroke: "#FBF7F0", strokeWidth: 2 }}
              connectNulls
            />
          )}
          {/* Speed is shown in tooltip only, km/h values can't share the power (W) axis */}
        </ComposedChart>
      </ResponsiveContainer>

      {/* Legend */}
      {(hasPacing || hasActual) && (
        <div className="flex flex-wrap items-center gap-3 px-1">
          <div className="flex items-center gap-1.5">
            <div className="h-0.5 w-4 rounded bg-vb-forest" />
            <span className="text-[10px] text-vb-text-muted">Elevation</span>
          </div>
          {hasPacing && showTargetPower && (
            <div className="flex items-center gap-1.5">
              <div className="h-0.5 w-4 rounded bg-vb-ochre" />
              <span className="text-[10px] text-vb-text-muted">Target Power</span>
            </div>
          )}
          {hasActual && showActualPower && (
            <div className="flex items-center gap-1.5">
              <svg width="16" height="4" className="shrink-0">
                <line x1="0" y1="2" x2="16" y2="2" stroke="#BB6647" strokeWidth="2" strokeDasharray="4 2" />
              </svg>
              <span className="text-[10px] text-vb-text-muted">Actual Power</span>
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
                  <span className="text-[10px] text-vb-text-muted">{z}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
