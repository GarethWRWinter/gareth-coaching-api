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
    <div className="rounded-md border border-vb-border-subtle bg-vb-surface p-3 text-sm shadow-[0_2px_8px_rgba(33,30,26,0.10)]">
      <p className="text-vb-text-dim">{formatDate(d.date)}</p>
      <p className="text-lg font-display font-light tracking-[-0.01em] text-vb-forest">{d.ftp}W</p>
      <p className="text-xs text-vb-text-muted capitalize">{d.source}</p>
    </div>
  );
}

export function FTPHistoryChart({ data, currentFTP }: FTPHistoryChartProps) {
  if (!data.length) {
    return (
      <p className="py-8 text-center text-sm text-vb-text-muted">
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
            <stop offset="5%" stopColor="#36513F" stopOpacity={0.3} />
            <stop offset="95%" stopColor="#36513F" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="#E4DCCE" />
        <XAxis
          dataKey="date"
          tickFormatter={formatDate}
          tick={{ fill: "#948D80", fontSize: 11 }}
          stroke="#D6CFC1"
        />
        <YAxis
          domain={[minFTP, maxFTP]}
          tick={{ fill: "#948D80", fontSize: 11 }}
          stroke="#D6CFC1"
          tickFormatter={(v) => `${v}W`}
        />
        <Tooltip content={<CustomTooltip />} />
        {currentFTP && (
          <ReferenceLine
            y={currentFTP}
            stroke="#7C95A3"
            strokeDasharray="3 3"
            label={{
              value: `Current: ${currentFTP}W`,
              position: "right",
              style: { fill: "#7C95A3", fontSize: 10 },
            }}
          />
        )}
        <Area
          type="stepAfter"
          dataKey="ftp"
          stroke="#36513F"
          strokeWidth={2}
          fill="url(#ftpGradient)"
          dot={{ r: 4, fill: "#36513F", stroke: "#FBF7F0" }}
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}
