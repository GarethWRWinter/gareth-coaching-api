"use client";

import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";
import { cn } from "@/lib/utils";

interface PowerCurveDataPoint {
  duration_seconds: number;
  duration_label: string;
  best_power: number;
  watts_per_kg?: number | null;
  all_time_power?: number | null;
  all_time_watts_per_kg?: number | null;
}

interface PowerCurveChartProps {
  data: PowerCurveDataPoint[];
  days?: number | null;
  className?: string;
}

const TICK_DURATIONS = [5, 30, 60, 300, 1200, 3600];
const TICK_LABELS: Record<number, string> = {
  5: "5s",
  30: "30s",
  60: "1min",
  300: "5min",
  1200: "20min",
  3600: "60min",
};

function PowerCurveTooltipContent({
  active,
  payload,
}: {
  active?: boolean;
  payload?: Array<{ payload: PowerCurveDataPoint }>;
}) {
  if (!active || !payload?.length) return null;
  const data = payload[0].payload;

  return (
    <div className="rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 shadow-xl">
      <p className="mb-1 text-xs font-medium text-slate-300">
        {data.duration_label}
      </p>
      <p className="text-sm font-mono font-medium text-amber-400">
        {Math.round(data.best_power)}W
        {data.watts_per_kg != null && data.watts_per_kg > 0 && (
          <span className="ml-1 text-xs text-slate-400">
            ({data.watts_per_kg.toFixed(2)} W/kg)
          </span>
        )}
      </p>
      {data.all_time_power != null && data.all_time_power > 0 &&
        Math.round(data.all_time_power) !== Math.round(data.best_power) && (
        <p className="mt-1 border-t border-slate-700 pt-1 text-xs font-mono text-slate-500">
          All-time: {Math.round(data.all_time_power)}W
          {data.all_time_watts_per_kg != null && (
            <span className="ml-1">({data.all_time_watts_per_kg.toFixed(2)} W/kg)</span>
          )}
        </p>
      )}
    </div>
  );
}

export function PowerCurveChart({ data, days, className }: PowerCurveChartProps) {
  const chartData = data.filter(
    (d) => d.best_power > 0 || (d.all_time_power && d.all_time_power > 0)
  );
  const hasAllTime = chartData.some(
    (d) => d.all_time_power && d.all_time_power > 0 &&
           Math.round(d.all_time_power) !== Math.round(d.best_power)
  );

  return (
    <div className={cn("rounded-xl bg-slate-900 p-4", className)}>
      <h3 className="mb-4 text-sm font-semibold text-slate-200">
        Power Duration Curve
      </h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart
          data={chartData}
          margin={{ top: 5, right: 10, left: 0, bottom: 5 }}
        >
          <CartesianGrid
            strokeDasharray="3 3"
            stroke="#334155"
            vertical={false}
          />
          <XAxis
            dataKey="duration_seconds"
            type="number"
            scale="log"
            domain={["dataMin", "dataMax"]}
            ticks={TICK_DURATIONS}
            tickFormatter={(v: number) => TICK_LABELS[v] || `${v}s`}
            stroke="#94a3b8"
            tick={{ fontSize: 11, fill: "#94a3b8" }}
            tickLine={{ stroke: "#475569" }}
            axisLine={{ stroke: "#475569" }}
          />
          <YAxis
            stroke="#94a3b8"
            tick={{ fontSize: 11, fill: "#94a3b8" }}
            tickLine={{ stroke: "#475569" }}
            axisLine={{ stroke: "#475569" }}
            tickFormatter={(v: number) => `${v}W`}
            domain={[0, "auto"]}
          />
          <Tooltip
            content={<PowerCurveTooltipContent />}
            cursor={{ stroke: "#64748b", strokeDasharray: "4 4" }}
          />
          {/* All-time curve (behind, dashed) */}
          {hasAllTime && (
            <Line
              type="monotone"
              dataKey="all_time_power"
              name="All-time PB"
              stroke="#475569"
              strokeWidth={1.5}
              strokeDasharray="6 3"
              dot={{ r: 2, fill: "#475569", stroke: "#1e293b", strokeWidth: 1 }}
              activeDot={false}
              connectNulls
            />
          )}
          {/* Current form curve (primary) */}
          <Line
            type="monotone"
            dataKey="best_power"
            name={days ? `Last ${days}d` : "Best Power"}
            stroke="#f59e0b"
            strokeWidth={2.5}
            dot={{ r: 3, fill: "#f59e0b", stroke: "#1e293b", strokeWidth: 1 }}
            activeDot={{ r: 5, fill: "#f59e0b", stroke: "#fbbf24" }}
            connectNulls
          />
        </LineChart>
      </ResponsiveContainer>
      {/* Legend */}
      {hasAllTime && (
        <div className="mt-2 flex items-center gap-4 text-[10px] text-slate-500">
          <span className="flex items-center gap-1.5">
            <span className="inline-block h-0.5 w-4 rounded bg-amber-500" />
            Current form ({days}d)
          </span>
          <span className="flex items-center gap-1.5">
            <svg width="16" height="4" className="shrink-0">
              <line x1="0" y1="2" x2="16" y2="2" stroke="#475569" strokeWidth="1.5" strokeDasharray="4 2" />
            </svg>
            All-time PB
          </span>
        </div>
      )}
    </div>
  );
}
