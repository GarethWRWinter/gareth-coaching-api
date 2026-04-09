"use client";

import { useMemo } from "react";
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
    <div className="rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 shadow-xl">
      <p className="mb-1.5 text-xs font-medium text-slate-300">
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
            <span className="text-slate-400">{entry.name}</span>
          </span>
          <span className="font-mono font-medium text-slate-100">
            {Math.round(entry.value)}
          </span>
        </div>
      ))}
    </div>
  );
}

export function PMCChart({ data, dateRange, className }: PMCChartProps) {
  // Calculate appropriate tick indices to avoid duplicate/overlapping labels
  const ticks = useMemo(() => {
    if (data.length === 0) return [];

    let targetTicks: number;
    switch (dateRange) {
      case "1m":
        targetTicks = 8; // roughly every ~4 days
        break;
      case "3m":
        targetTicks = 10; // roughly every ~9 days
        break;
      case "6m":
        targetTicks = 10; // roughly every ~18 days
        break;
      case "1y":
        targetTicks = 12; // monthly
        break;
      default:
        targetTicks = 12;
    }

    const step = Math.max(1, Math.floor(data.length / targetTicks));
    const tickDates: string[] = [];
    for (let i = 0; i < data.length; i += step) {
      tickDates.push(data[i].date);
    }
    // Always include the last date
    const lastDate = data[data.length - 1].date;
    if (tickDates[tickDates.length - 1] !== lastDate) {
      tickDates.push(lastDate);
    }
    return tickDates;
  }, [data, dateRange]);

  return (
    <div className={cn("rounded-xl bg-slate-900 p-4", className)}>
      <h3 className="mb-4 text-sm font-semibold text-slate-200">
        Performance Management Chart
      </h3>
      <ResponsiveContainer width="100%" height={350}>
        <ComposedChart
          data={data}
          margin={{ top: 5, right: 10, left: 0, bottom: 5 }}
        >
          <CartesianGrid
            strokeDasharray="3 3"
            stroke="#334155"
            vertical={false}
          />
          <XAxis
            dataKey="date"
            tickFormatter={(val: string) => formatXAxisDate(val, dateRange)}
            ticks={ticks}
            stroke="#94a3b8"
            tick={{ fontSize: 11, fill: "#94a3b8" }}
            tickLine={{ stroke: "#475569" }}
            axisLine={{ stroke: "#475569" }}
          />
          <YAxis
            yAxisId="metrics"
            stroke="#94a3b8"
            tick={{ fontSize: 11, fill: "#94a3b8" }}
            tickLine={{ stroke: "#475569" }}
            axisLine={{ stroke: "#475569" }}
          />
          <YAxis
            yAxisId="tss"
            orientation="right"
            stroke="#94a3b8"
            tick={{ fontSize: 11, fill: "#94a3b8" }}
            tickLine={{ stroke: "#475569" }}
            axisLine={{ stroke: "#475569" }}
            domain={[0, "auto"]}
            hide
          />
          <Tooltip
            content={<PMCTooltipContent />}
            cursor={{ stroke: "#64748b", strokeDasharray: "4 4" }}
          />
          <Legend
            wrapperStyle={{ paddingTop: 12, fontSize: 12 }}
            iconType="circle"
            iconSize={8}
          />

          {/* TSS bars at the bottom */}
          <Bar
            yAxisId="tss"
            dataKey="tss"
            name="TSS"
            fill="#475569"
            opacity={0.5}
            barSize={3}
            radius={[1, 1, 0, 0]}
          />

          {/* TSB / Form as an area */}
          <Area
            yAxisId="metrics"
            type="monotone"
            dataKey="tsb"
            name="Form"
            stroke="#22c55e"
            fill="#22c55e"
            fillOpacity={0.1}
            strokeWidth={1.5}
            dot={false}
            activeDot={{ r: 3, fill: "#22c55e" }}
          />

          {/* CTL / Fitness line */}
          <Line
            yAxisId="metrics"
            type="monotone"
            dataKey="ctl"
            name="Fitness"
            stroke="#3b82f6"
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 4, fill: "#3b82f6" }}
          />

          {/* ATL / Fatigue line */}
          <Line
            yAxisId="metrics"
            type="monotone"
            dataKey="atl"
            name="Fatigue"
            stroke="#ef4444"
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 4, fill: "#ef4444" }}
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}
