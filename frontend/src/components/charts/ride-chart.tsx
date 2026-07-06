"use client";

import {
  ResponsiveContainer,
  ComposedChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid,
} from "recharts";
import { cn } from "@/lib/utils";
import { SERIES } from "@/lib/palette";

const MONO = "IBM Plex Mono, ui-monospace, SFMono-Regular, monospace";
const TICK = { fontSize: 11, fill: SERIES.grey, fontFamily: MONO };

interface RideDataPoint {
  elapsed_seconds: number;
  power: number | null;
  heart_rate: number | null;
  cadence: number | null;
}

interface RideChartProps {
  data: RideDataPoint[];
  className?: string;
}

function formatElapsedTime(seconds: number): string {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = Math.floor(seconds % 60);
  if (h > 0) {
    return `${h}:${String(m).padStart(2, "0")}`;
  }
  return `${m}:${String(s).padStart(2, "0")}`;
}

function RideTooltipContent({
  active,
  payload,
  label,
}: {
  active?: boolean;
  payload?: Array<{ name: string; value: number | null; color: string }>;
  label?: number;
}) {
  if (!active || !payload || label == null) return null;

  return (
    <div className="rounded-sm border border-vb-border bg-vb-surface px-3 py-2">
      <p className="f-kicker mb-1.5 text-vb-text-muted">
        {formatElapsedTime(label)}
      </p>
      {payload.map((entry) => {
        if (entry.value == null) return null;
        const unit =
          entry.name === "Power"
            ? "W"
            : entry.name === "Heart rate"
              ? " bpm"
              : " rpm";
        return (
          <div
            key={entry.name}
            className="flex items-center justify-between gap-4 text-sm"
          >
            <span className="flex items-center gap-1.5">
              <span
                className="inline-block h-2 w-2 rounded-full"
                style={{ backgroundColor: entry.color }}
              />
              <span className="text-vb-text-dim">{entry.name}</span>
            </span>
            <span className="f-data font-medium text-vb-text">
              {Math.round(entry.value)}
              {unit}
            </span>
          </div>
        );
      })}
    </div>
  );
}

export function RideChart({ data, className }: RideChartProps) {
  // Determine if ride is longer than 1 hour for axis formatting
  const maxSeconds = data.length > 0 ? data[data.length - 1].elapsed_seconds : 0;
  const tickInterval = maxSeconds > 3600 ? 600 : maxSeconds > 600 ? 60 : 30;

  return (
    <div
      className={cn(
        "rounded-sm border border-vb-border-subtle bg-vb-surface p-4",
        className
      )}
    >
      <h3 className="f-kicker mb-4 text-vb-text-muted">
        Power · Heart rate · Cadence
      </h3>
      <ResponsiveContainer width="100%" height={350}>
        <ComposedChart
          data={data}
          margin={{ top: 5, right: 10, left: 0, bottom: 5 }}
        >
          <CartesianGrid stroke={SERIES.hairline} vertical={false} />
          <XAxis
            dataKey="elapsed_seconds"
            tickFormatter={formatElapsedTime}
            stroke={SERIES.hairline}
            tick={TICK}
            tickLine={{ stroke: SERIES.hairline }}
            axisLine={{ stroke: SERIES.hairline }}
            interval="preserveStartEnd"
            minTickGap={50}
            type="number"
            domain={[0, "auto"]}
          />

          {/* Power axis (left) */}
          <YAxis
            yAxisId="power"
            orientation="left"
            stroke={SERIES.hairline}
            tick={TICK}
            tickLine={{ stroke: SERIES.hairline }}
            axisLine={{ stroke: SERIES.hairline }}
            tickFormatter={(v: number) => `${v}W`}
            domain={[0, "auto"]}
          />

          {/* Heart rate axis (right) */}
          <YAxis
            yAxisId="hr"
            orientation="right"
            stroke={SERIES.hairline}
            tick={TICK}
            tickLine={{ stroke: SERIES.hairline }}
            axisLine={{ stroke: SERIES.hairline }}
            tickFormatter={(v: number) => `${v}`}
            domain={[0, "auto"]}
          />

          {/* Cadence axis (hidden) */}
          <YAxis
            yAxisId="cadence"
            hide
            domain={[0, "auto"]}
          />

          <Tooltip
            content={<RideTooltipContent />}
            cursor={{ stroke: SERIES.grey, strokeDasharray: "4 4" }}
          />
          <Legend
            wrapperStyle={{
              paddingTop: 12,
              fontSize: 11,
              fontFamily: MONO,
              color: SERIES.grey,
            }}
            iconType="circle"
            iconSize={7}
          />

          <Line
            yAxisId="power"
            type="monotone"
            dataKey="power"
            name="Power"
            stroke={SERIES.ink}
            strokeWidth={1.5}
            dot={false}
            connectNulls={false}
            activeDot={{ r: 3, fill: SERIES.ink }}
          />

          <Line
            yAxisId="hr"
            type="monotone"
            dataKey="heart_rate"
            name="Heart rate"
            stroke={SERIES.amber}
            strokeWidth={1.5}
            dot={false}
            connectNulls={false}
            activeDot={{ r: 3, fill: SERIES.amber }}
          />

          <Line
            yAxisId="cadence"
            type="monotone"
            dataKey="cadence"
            name="Cadence"
            stroke={SERIES.grey}
            strokeWidth={1}
            strokeOpacity={0.7}
            dot={false}
            connectNulls={false}
            activeDot={{ r: 3, fill: SERIES.grey }}
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}
