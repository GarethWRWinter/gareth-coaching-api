"use client";

import {
  ResponsiveContainer,
  ComposedChart,
  Line,
  Area,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid,
} from "recharts";
import { cn } from "@/lib/utils";

interface PMCDataPoint {
  date: string;
  ctl: number;
  atl: number;
  tsb: number;
  tss: number;
}

interface PMCChartProps {
  data: PMCDataPoint[];
  dateRange?: string;
  className?: string;
}

function formatXAxisDate(dateStr: string, dateRange?: string): string {
  const d = new Date(dateStr);
  if (dateRange === "1m") {
    return d.toLocaleDateString("en-US", { month: "short", day: "numeric" });
  }
  if (dateRange === "3m" || dateRange === "6m") {
    return d.toLocaleDateString("en-US", { month: "short", day: "numeric" });
  }
  // For 1y and all, show month + year
  return d.toLocaleDateString("en-US", { month: "short", year: "2-digit" });
}

function PMCTooltipContent({
  active,
  payload,
  label,
}: {
  active?: boolean;
  payload?: Array<{ name: string; value: number; color: string }>;
  label?: string;
}) {
  if (!active || !payload || !label) return null;

  const formattedDate = new Date(label).toLocaleDateString("en-US", {
    weekday: "short",
    month: "short",
    day: "numeric",
    year: "numeric",
  });

  return (
    <div className="rounded-md border border-vb-border-subtle bg-vb-surface px-3 py-2 shadow-[0_2px_8px_rgba(33,30,26,0.10)]">
      <p className="mb-1.5 text-xs font-medium text-vb-text-dim">
        {formattedDate}
      </p>
      {payload.map((entry) => (
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
          <span className="font-medium tabular-nums text-vb-text">
            {Math.round(entry.value)}
          </span>
        </div>
      ))}
    </div>
  );
}

export function PMCChart({ data, dateRange, className }: PMCChartProps) {
  return (
    <div className={cn("rounded-md border border-vb-border-subtle bg-vb-surface p-5", className)}>
      <h3 className="mb-4 text-[11px] font-medium uppercase tracking-[0.16em] text-vb-text-muted">
        Performance Management Chart
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
            dataKey="date"
            tickFormatter={(val: string) => formatXAxisDate(val, dateRange)}
            interval="preserveStartEnd"
            minTickGap={48}
            stroke="#D6CFC1"
            tick={{ fontSize: 11, fill: "#948D80" }}
            tickLine={{ stroke: "#D6CFC1" }}
            axisLine={{ stroke: "#D6CFC1" }}
          />
          <YAxis
            yAxisId="metrics"
            stroke="#D6CFC1"
            tick={{ fontSize: 11, fill: "#948D80" }}
            tickLine={{ stroke: "#D6CFC1" }}
            axisLine={{ stroke: "#D6CFC1" }}
          />
          <YAxis
            yAxisId="tss"
            orientation="right"
            domain={[0, "auto"]}
            hide
          />
          <Tooltip
            content={<PMCTooltipContent />}
            cursor={{ stroke: "#BCB3A3", strokeDasharray: "4 4" }}
          />
          <Legend
            wrapperStyle={{ paddingTop: 12, fontSize: 12, color: "#615B50" }}
            iconType="circle"
            iconSize={8}
          />

          {/* TSS bars at the bottom — sage */}
          <Bar
            yAxisId="tss"
            dataKey="tss"
            name="TSS"
            fill="#C3CDBC"
            opacity={0.7}
            barSize={3}
            radius={[1, 1, 0, 0]}
          />

          {/* TSB / Form as an area — dusty blue */}
          <Area
            yAxisId="metrics"
            type="monotone"
            dataKey="tsb"
            name="Form"
            stroke="#7C95A3"
            fill="#7C95A3"
            fillOpacity={0.12}
            strokeWidth={1.5}
            dot={false}
            activeDot={{ r: 3, fill: "#7C95A3" }}
          />

          {/* CTL / Fitness line — forest */}
          <Line
            yAxisId="metrics"
            type="monotone"
            dataKey="ctl"
            name="Fitness"
            stroke="#36513F"
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 4, fill: "#36513F" }}
          />

          {/* ATL / Fatigue line — clay */}
          <Line
            yAxisId="metrics"
            type="monotone"
            dataKey="atl"
            name="Fatigue"
            stroke="#BB6647"
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 4, fill: "#BB6647" }}
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}
