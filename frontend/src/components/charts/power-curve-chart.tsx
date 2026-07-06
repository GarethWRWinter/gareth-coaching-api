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
import { SERIES } from "@/lib/palette";

const MONO = "IBM Plex Mono, ui-monospace, SFMono-Regular, monospace";
const TICK = { fontSize: 11, fill: SERIES.grey, fontFamily: MONO };

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

function isAtPB(p: PowerCurveDataPoint): boolean {
  return (
    p.all_time_power != null &&
    p.all_time_power > 0 &&
    p.best_power > 0 &&
    Math.round(p.best_power) >= Math.round(p.all_time_power)
  );
}

/** Flamme marker where current form equals the all-time PB. */
function PBDot(props: any) {
  const { cx, cy, payload, index } = props;
  if (cx == null || cy == null) return null;
  const pb = isAtPB(payload);
  return (
    <circle
      key={index}
      cx={cx}
      cy={cy}
      r={pb ? 4 : 3}
      fill={pb ? SERIES.flamme : SERIES.ink}
      stroke={SERIES.paper}
      strokeWidth={1}
    />
  );
}

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
    <div className="rounded-sm border border-vb-border bg-vb-surface px-3 py-2">
      <p className="f-kicker mb-1 text-vb-text-muted">
        {data.duration_label}
      </p>
      <p className="f-data text-sm font-medium text-vb-text">
        {Math.round(data.best_power)}W
        {data.watts_per_kg != null && data.watts_per_kg > 0 && (
          <span className="ml-1 text-xs text-vb-text-dim">
            ({data.watts_per_kg.toFixed(2)} W/kg)
          </span>
        )}
      </p>
      {isAtPB(data) && (
        <p className="f-kicker mt-1 text-vb-red">All-time best</p>
      )}
      {data.all_time_power != null && data.all_time_power > 0 &&
        Math.round(data.all_time_power) !== Math.round(data.best_power) && (
        <p className="f-data mt-1 border-t border-vb-border-subtle pt-1 text-xs text-vb-text-muted">
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
    <div
      className={cn(
        "rounded-sm border border-vb-border-subtle bg-vb-surface p-4",
        className
      )}
    >
      <h3 className="f-kicker mb-4 text-vb-text-muted">
        Best power by duration
      </h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart
          data={chartData}
          margin={{ top: 5, right: 10, left: 0, bottom: 5 }}
        >
          <CartesianGrid stroke={SERIES.hairline} vertical={false} />
          <XAxis
            dataKey="duration_seconds"
            type="number"
            scale="log"
            domain={["dataMin", "dataMax"]}
            ticks={TICK_DURATIONS}
            tickFormatter={(v: number) => TICK_LABELS[v] || `${v}s`}
            stroke={SERIES.hairline}
            tick={TICK}
            tickLine={{ stroke: SERIES.hairline }}
            axisLine={{ stroke: SERIES.hairline }}
          />
          <YAxis
            stroke={SERIES.hairline}
            tick={TICK}
            tickLine={{ stroke: SERIES.hairline }}
            axisLine={{ stroke: SERIES.hairline }}
            tickFormatter={(v: number) => `${v}W`}
            domain={[0, "auto"]}
          />
          <Tooltip
            content={<PowerCurveTooltipContent />}
            cursor={{ stroke: SERIES.grey, strokeDasharray: "4 4" }}
          />
          {/* All-time curve (behind, grey dashed) */}
          {hasAllTime && (
            <Line
              type="monotone"
              dataKey="all_time_power"
              name="All-time PB"
              stroke={SERIES.grey}
              strokeWidth={1.5}
              strokeDasharray="6 3"
              dot={{ r: 2, fill: SERIES.grey, stroke: SERIES.paper, strokeWidth: 1 }}
              activeDot={false}
              connectNulls
            />
          )}
          {/* Current form curve (primary, ink; flamme where it touches the PB) */}
          <Line
            type="monotone"
            dataKey="best_power"
            name={days ? `Last ${days}d` : "Best power"}
            stroke={SERIES.ink}
            strokeWidth={1.5}
            dot={<PBDot />}
            activeDot={{ r: 5, fill: SERIES.ink, stroke: SERIES.ink }}
            connectNulls
          />
        </LineChart>
      </ResponsiveContainer>
      {/* Legend */}
      {hasAllTime && (
        <div className="mt-2 flex items-center gap-4 font-mono text-[10px] text-vb-text-muted">
          <span className="flex items-center gap-1.5">
            <span className="inline-block h-px w-4 bg-vb-text" />
            Current form ({days}d)
          </span>
          <span className="flex items-center gap-1.5">
            <svg width="16" height="4" className="shrink-0">
              <line x1="0" y1="2" x2="16" y2="2" stroke={SERIES.grey} strokeWidth="1.5" strokeDasharray="4 2" />
            </svg>
            All-time PB
          </span>
          <span className="flex items-center gap-1.5">
            <span className="inline-block h-2 w-2 rounded-full bg-vb-red" />
            At your best
          </span>
        </div>
      )}
    </div>
  );
}
