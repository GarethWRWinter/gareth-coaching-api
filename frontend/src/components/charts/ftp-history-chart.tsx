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
import { SERIES } from "@/lib/palette";

const MONO = "IBM Plex Mono, ui-monospace, SFMono-Regular, monospace";
const TICK = { fontSize: 11, fill: SERIES.grey, fontFamily: MONO };

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
    <div className="rounded-sm border border-vb-border bg-vb-surface p-3 text-sm">
      <p className="f-kicker text-vb-text-muted">{formatDate(d.date)}</p>
      <p className="f-data mt-1 text-lg font-semibold text-vb-text">{d.ftp}W</p>
      <p className="text-xs capitalize text-vb-text-muted">{d.source}</p>
    </div>
  );
}

export function FTPHistoryChart({ data, currentFTP }: FTPHistoryChartProps) {
  if (!data.length) {
    return (
      <p className="py-8 text-center text-sm text-vb-text-muted">
        No FTP history yet. Test, or let a hard ride reveal it.
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
        <CartesianGrid stroke={SERIES.hairline} vertical={false} />
        <XAxis
          dataKey="date"
          tickFormatter={formatDate}
          tick={TICK}
          stroke={SERIES.hairline}
        />
        <YAxis
          domain={[minFTP, maxFTP]}
          tick={TICK}
          stroke={SERIES.hairline}
          tickFormatter={(v) => `${v}W`}
        />
        <Tooltip content={<CustomTooltip />} />
        {currentFTP && (
          <ReferenceLine
            y={currentFTP}
            stroke={SERIES.flamme}
            strokeDasharray="3 3"
            label={{
              value: `Now: ${currentFTP}W`,
              position: "right",
              style: { fill: SERIES.flamme, fontSize: 10, fontFamily: MONO },
            }}
          />
        )}
        <Area
          type="stepAfter"
          dataKey="ftp"
          stroke={SERIES.ink}
          strokeWidth={1.5}
          fill={SERIES.ink}
          fillOpacity={0.04}
          dot={{ r: 3, fill: SERIES.ink, stroke: SERIES.paper }}
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}
