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
import { SERIES } from "@/lib/palette";

const MONO = "IBM Plex Mono, ui-monospace, SFMono-Regular, monospace";
const TICK = { fontSize: 11, fill: SERIES.grey, fontFamily: MONO };

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
    return d.toLocaleDateString("en-GB", { month: "short", day: "numeric" });
  }
  if (dateRange === "3m" || dateRange === "6m") {
    return d.toLocaleDateString("en-GB", { month: "short", day: "numeric" });
  }
  // For 1y and all, show month + year
  return d.toLocaleDateString("en-GB", { month: "short", year: "2-digit" });
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

  const formattedDate = new Date(label).toLocaleDateString("en-GB", {
    weekday: "short",
    month: "short",
    day: "numeric",
    year: "numeric",
  });

  return (
    <div className="rounded-sm border border-vb-border bg-vb-surface px-3 py-2">
      <p className="f-kicker mb-1.5 text-vb-text-muted">{formattedDate}</p>
      {payload.map((entry) => (
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
          </span>
        </div>
      ))}
    </div>
  );
}

export function PMCChart({ data, dateRange, className }: PMCChartProps) {
  return (
    <div
      className={cn(
        "rounded-sm border border-vb-border-subtle bg-vb-surface p-5",
        className
      )}
    >
      <h3 className="f-kicker mb-4 text-vb-text-muted">
        Fitness · Fatigue · Form
      </h3>
      <ResponsiveContainer width="100%" height={350}>
        <ComposedChart
          data={data}
          margin={{ top: 5, right: 10, left: 0, bottom: 5 }}
        >
          <CartesianGrid stroke={SERIES.hairline} vertical={false} />
          <XAxis
            dataKey="date"
            tickFormatter={(val: string) => formatXAxisDate(val, dateRange)}
            interval="preserveStartEnd"
            minTickGap={48}
            stroke={SERIES.hairline}
            tick={TICK}
            tickLine={{ stroke: SERIES.hairline }}
            axisLine={{ stroke: SERIES.hairline }}
          />
          <YAxis
            yAxisId="metrics"
            stroke={SERIES.hairline}
            tick={TICK}
            tickLine={{ stroke: SERIES.hairline }}
            axisLine={{ stroke: SERIES.hairline }}
          />
          <YAxis
            yAxisId="tss"
            orientation="right"
            domain={[0, "auto"]}
            hide
          />
          <Tooltip
            content={<PMCTooltipContent />}
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

          {/* TSS bars at the bottom, quiet context */}
          <Bar
            yAxisId="tss"
            dataKey="tss"
            name="TSS"
            fill={SERIES.grey}
            opacity={0.3}
            barSize={2}
            radius={[0, 0, 0, 0]}
          />

          {/* TSB / Form — the story, flamme */}
          <Area
            yAxisId="metrics"
            type="monotone"
            dataKey="tsb"
            name="Form"
            stroke={SERIES.flamme}
            fill={SERIES.flamme}
            fillOpacity={0.06}
            strokeWidth={1.5}
            dot={false}
            activeDot={{ r: 3, fill: SERIES.flamme }}
          />

          {/* CTL / Fitness — the primary line, ink */}
          <Line
            yAxisId="metrics"
            type="monotone"
            dataKey="ctl"
            name="Fitness"
            stroke={SERIES.ink}
            strokeWidth={1.5}
            dot={false}
            activeDot={{ r: 3.5, fill: SERIES.ink }}
          />

          {/* ATL / Fatigue — context, grey */}
          <Line
            yAxisId="metrics"
            type="monotone"
            dataKey="atl"
            name="Fatigue"
            stroke={SERIES.grey}
            strokeWidth={1.5}
            dot={false}
            activeDot={{ r: 3.5, fill: SERIES.grey }}
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}
