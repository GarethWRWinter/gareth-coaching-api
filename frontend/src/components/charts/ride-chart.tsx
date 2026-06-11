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
    <div className="rounded-md border border-vb-border-subtle bg-vb-surface px-3 py-2 shadow-[0_2px_8px_rgba(33,30,26,0.10)]">
      <p className="mb-1.5 text-xs font-medium text-vb-text-dim">
        {formatElapsedTime(label)}
      </p>
      {payload.map((entry) => {
        if (entry.value == null) return null;
        const unit =
          entry.name === "Power"
            ? "W"
            : entry.name === "Heart Rate"
              ? " bpm"
              : " rpm";
        return (
          <div
            key={entry.name}
            className="flex items-center justify-between gap-4 text-sm"
          >
            <span className="flex items-center gap-1.5">
              <span
                className="inline-block h-2.5 w-2.5 rounded-full"
                style={{ backgroundColor: entry.color }}
              />
              <span className="text-vb-text-dim">{entry.name}</span>
            </span>
            <span className="font-mono font-medium text-vb-text">
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
    <div className={cn("rounded-md border border-vb-border-subtle bg-vb-surface p-4", className)}>
      <h3 className="mb-4 text-[11px] font-medium uppercase tracking-[0.16em] text-vb-text-muted">
        Ride Data
      </h3>
      <ResponsiveContainer width="100%" height={350}>
        <ComposedChart
          data={data}
          margin={{ top: 5, right: 10, left: 0, bottom: 5 }}
        >
          <CartesianGrid
            strokeDasharray="3 3"
            stroke="#E4DCCE"
            vertical={false}
          />
          <XAxis
            dataKey="elapsed_seconds"
            tickFormatter={formatElapsedTime}
            stroke="#D6CFC1"
            tick={{ fontSize: 11, fill: "#948D80" }}
            tickLine={{ stroke: "#D6CFC1" }}
            axisLine={{ stroke: "#D6CFC1" }}
            interval="preserveStartEnd"
            minTickGap={50}
            type="number"
            domain={[0, "auto"]}
          />

          {/* Power axis (left) */}
          <YAxis
            yAxisId="power"
            orientation="left"
            stroke="#D6CFC1"
            tick={{ fontSize: 11, fill: "#36513F" }}
            tickLine={{ stroke: "#D6CFC1" }}
            axisLine={{ stroke: "#D6CFC1" }}
            tickFormatter={(v: number) => `${v}W`}
            domain={[0, "auto"]}
          />

          {/* Heart rate axis (right) */}
          <YAxis
            yAxisId="hr"
            orientation="right"
            stroke="#D6CFC1"
            tick={{ fontSize: 11, fill: "#BB6647" }}
            tickLine={{ stroke: "#D6CFC1" }}
            axisLine={{ stroke: "#D6CFC1" }}
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
            cursor={{ stroke: "#BCB3A3", strokeDasharray: "4 4" }}
          />
          <Legend
            wrapperStyle={{ paddingTop: 12, fontSize: 12 }}
            iconType="circle"
            iconSize={8}
          />

          <Line
            yAxisId="power"
            type="monotone"
            dataKey="power"
            name="Power"
            stroke="#36513F"
            strokeWidth={1.5}
            dot={false}
            connectNulls={false}
            activeDot={{ r: 3, fill: "#36513F" }}
          />

          <Line
            yAxisId="hr"
            type="monotone"
            dataKey="heart_rate"
            name="Heart Rate"
            stroke="#BB6647"
            strokeWidth={1.5}
            dot={false}
            connectNulls={false}
            activeDot={{ r: 3, fill: "#BB6647" }}
          />

          <Line
            yAxisId="cadence"
            type="monotone"
            dataKey="cadence"
            name="Cadence"
            stroke="#7C95A3"
            strokeWidth={1}
            strokeOpacity={0.7}
            dot={false}
            connectNulls={false}
            activeDot={{ r: 3, fill: "#7C95A3" }}
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}
