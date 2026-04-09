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
    <div className="rounded-lg border border-slate-700 bg-slate-800 p-3 text-sm shadow-lg">
      <p className="mb-1 font-medium text-white">
        Week of {formatWeek(d.week_start)}
      </p>
      <p className="text-blue-400">TSS: {Math.round(d.total_tss)}</p>
      <p className="text-slate-300">Rides: {d.ride_count}</p>
      <p className="text-slate-300">
        Duration: {formatDuration(d.total_duration_seconds)}
      </p>
      {d.avg_intensity_factor && (
        <p className="text-amber-400">
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
    if (tss >= 500) return "#ef4444"; // red - very high
    if (tss >= 350) return "#f97316"; // orange - high
    if (tss >= 200) return "#3b82f6"; // blue - moderate
    return "#6366f1"; // indigo - low
  };

  return (
    <ResponsiveContainer width="100%" height={250}>
      <BarChart data={chartData} margin={{ top: 5, right: 10, bottom: 5, left: -10 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
        <XAxis
          dataKey="label"
          tick={{ fill: "#94a3b8", fontSize: 11 }}
          stroke="#475569"
        />
        <YAxis
          tick={{ fill: "#94a3b8", fontSize: 11 }}
          stroke="#475569"
          label={{
            value: "TSS",
            angle: -90,
            position: "insideLeft",
            style: { fill: "#94a3b8", fontSize: 11 },
          }}
        />
        <Tooltip content={<CustomTooltip />} />
        <Bar
          dataKey="total_tss"
          radius={[4, 4, 0, 0]}
          fill="#3b82f6"
        />
      </BarChart>
    </ResponsiveContainer>
  );
}
