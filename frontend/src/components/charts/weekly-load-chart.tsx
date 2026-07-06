"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { SERIES } from "@/lib/palette";

const MONO = "IBM Plex Mono, ui-monospace, SFMono-Regular, monospace";
const TICK = { fontSize: 11, fill: SERIES.grey, fontFamily: MONO };

interface WeeklyLoadData {
  week_start: string;
  total_tss: number;
  ride_count: number;
  total_duration_seconds: number;
  avg_intensity_factor: number | null;
}

interface WeeklyLoadChartProps {
  data: WeeklyLoadData[];
}

function formatWeek(dateStr: string) {
  const d = new Date(dateStr + "T00:00:00");
  return d.toLocaleDateString("en-GB", { day: "numeric", month: "short" });
}

function formatDuration(seconds: number) {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  return h > 0 ? `${h}h ${m}m` : `${m}m`;
}

function CustomTooltip({ active, payload }: any) {
  if (!active || !payload?.[0]) return null;
  const d = payload[0].payload;
  return (
    <div className="rounded-sm border border-vb-border bg-vb-surface p-3 text-sm">
      <p className="f-kicker mb-1 text-vb-text-muted">
        Week of {formatWeek(d.week_start)}
      </p>
      <p className="f-data font-medium text-vb-text">
        TSS {Math.round(d.total_tss)}
      </p>
      <p className="text-xs text-vb-text-dim">Rides: {d.ride_count}</p>
      <p className="text-xs text-vb-text-dim">
        Duration: {formatDuration(d.total_duration_seconds)}
      </p>
      {d.avg_intensity_factor && (
        <p className="text-xs text-vb-text-dim">
          Avg IF: {d.avg_intensity_factor.toFixed(2)}
        </p>
      )}
    </div>
  );
}

export function WeeklyLoadChart({ data }: WeeklyLoadChartProps) {
  const chartData = data.map((w) => ({
    ...w,
    label: formatWeek(w.week_start),
  }));

  return (
    <ResponsiveContainer width="100%" height={250}>
      <BarChart data={chartData} margin={{ top: 5, right: 10, bottom: 5, left: -10 }}>
        <CartesianGrid stroke={SERIES.hairline} vertical={false} />
        <XAxis
          dataKey="label"
          tick={TICK}
          stroke={SERIES.hairline}
        />
        <YAxis
          tick={TICK}
          stroke={SERIES.hairline}
          label={{
            value: "TSS",
            angle: -90,
            position: "insideLeft",
            style: { fill: SERIES.grey, fontSize: 11, fontFamily: MONO },
          }}
        />
        <Tooltip content={<CustomTooltip />} cursor={{ fill: SERIES.chalk }} />
        {/* Ink bars; the latest week burns flamme */}
        <Bar dataKey="total_tss" radius={[0, 0, 0, 0]}>
          {chartData.map((entry, i) => (
            <Cell
              key={entry.week_start}
              fill={i === chartData.length - 1 ? SERIES.flamme : SERIES.ink}
            />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
