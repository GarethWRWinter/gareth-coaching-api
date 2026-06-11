"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

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
    <div className="rounded-md border border-vb-border-subtle bg-vb-surface p-3 text-sm shadow-[0_2px_8px_rgba(33,30,26,0.10)]">
      <p className="mb-1 font-medium text-vb-text">
        Week of {formatWeek(d.week_start)}
      </p>
      <p className="text-vb-forest">TSS: {Math.round(d.total_tss)}</p>
      <p className="text-vb-text-dim">Rides: {d.ride_count}</p>
      <p className="text-vb-text-dim">
        Duration: {formatDuration(d.total_duration_seconds)}
      </p>
      {d.avg_intensity_factor && (
        <p className="text-vb-clay">
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

  // Color bars by TSS intensity
  const getBarColor = (tss: number) => {
    if (tss >= 500) return "#A24E36"; // very high
    if (tss >= 350) return "#D2855B"; // high
    if (tss >= 200) return "#C7A458"; // moderate
    return "#C3CDBC"; // low
  };

  return (
    <ResponsiveContainer width="100%" height={250}>
      <BarChart data={chartData} margin={{ top: 5, right: 10, bottom: 5, left: -10 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#E4DCCE" />
        <XAxis
          dataKey="label"
          tick={{ fill: "#948D80", fontSize: 11 }}
          stroke="#D6CFC1"
        />
        <YAxis
          tick={{ fill: "#948D80", fontSize: 11 }}
          stroke="#D6CFC1"
          label={{
            value: "TSS",
            angle: -90,
            position: "insideLeft",
            style: { fill: "#948D80", fontSize: 11 },
          }}
        />
        <Tooltip content={<CustomTooltip />} />
        <Bar
          dataKey="total_tss"
          radius={[4, 4, 0, 0]}
          fill="#C3CDBC"
        />
      </BarChart>
    </ResponsiveContainer>
  );
}
