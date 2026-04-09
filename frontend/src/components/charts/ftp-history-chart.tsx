"use client";

import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  ReferenceLine,
} from "recharts";

interface FTPHistoryData {
  date: string;
  ftp: number;
  source: string;
}

interface FTPHistoryChartProps {
  data: FTPHistoryData[];
  currentFTP: number | null;
}

function formatDate(dateStr: string) {
  const d = new Date(dateStr + "T00:00:00");
  return d.toLocaleDateString("en-GB", { month: "short", year: "2-digit" });
}

function CustomTooltip({ active, payload }: any) {
  if (!active || !payload?.[0]) return null;
  const d = payload[0].payload;
  return (
    <div className="rounded-lg border border-slate-700 bg-slate-800 p-3 text-sm shadow-lg">
      <p className="text-slate-400">{formatDate(d.date)}</p>
      <p className="text-lg font-bold text-blue-400">{d.ftp}W</p>
      <p className="text-xs text-slate-500 capitalize">{d.source}</p>
    </div>
  );
}

export function FTPHistoryChart({ data, currentFTP }: FTPHistoryChartProps) {
  if (!data.length) {
    return (
      <p className="py-8 text-center text-sm text-slate-500">
        No FTP history available
      </p>
    );
  }

  // Extend data to include today if current FTP differs from last entry
  const chartData = [...data];
  if (
    currentFTP &&
    chartData.length > 0
  ) {
    const today = new Date().toISOString().split("T")[0];
    const last = chartData[chartData.length - 1];
    if (last.date !== today) {
      chartData.push({ date: today, ftp: currentFTP, source: "current" });
    }
  }

  const ftpValues = chartData.map((d) => d.ftp);
  const minFTP = Math.min(...ftpValues) - 20;
  const maxFTP = Math.max(...ftpValues) + 20;

  return (
    <ResponsiveContainer width="100%" height={200}>
      <AreaChart
        data={chartData}
        margin={{ top: 5, right: 10, bottom: 5, left: -10 }}
      >
        <defs>
          <linearGradient id="ftpGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
            <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
        <XAxis
          dataKey="date"
          tickFormatter={formatDate}
          tick={{ fill: "#94a3b8", fontSize: 11 }}
          stroke="#475569"
        />
        <YAxis
          domain={[minFTP, maxFTP]}
          tick={{ fill: "#94a3b8", fontSize: 11 }}
          stroke="#475569"
          tickFormatter={(v) => `${v}W`}
        />
        <Tooltip content={<CustomTooltip />} />
        {currentFTP && (
          <ReferenceLine
            y={currentFTP}
            stroke="#6366f1"
            strokeDasharray="3 3"
            label={{
              value: `Current: ${currentFTP}W`,
              position: "right",
              style: { fill: "#6366f1", fontSize: 10 },
            }}
          />
        )}
        <Area
          type="stepAfter"
          dataKey="ftp"
          stroke="#3b82f6"
          strokeWidth={2}
          fill="url(#ftpGradient)"
          dot={{ r: 4, fill: "#3b82f6", stroke: "#1e3a5f" }}
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}
